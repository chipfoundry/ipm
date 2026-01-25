#!/usr/bin/env python3
"""
Data validation script to check which IPs have valid GitHub repositories.
This script will help identify data quality issues in the IP database.
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import urlparse

def connect_to_mongodb():
    """Connect to MongoDB using the MONGO_URI from .env"""
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/ipm")
    
    try:
        client = MongoClient(mongo_uri)
        # Test the connection
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB at {mongo_uri}")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please ensure MongoDB is running and the MONGO_URI is correct in your .env file.")
        sys.exit(1)

def validate_github_repository(repo_url):
    """Check if a GitHub repository exists"""
    if not repo_url.startswith("github.com/"):
        return False, "Not a GitHub repository"
    
    # Extract owner and repo name
    parts = repo_url[len("github.com/"):].split("/")
    if len(parts) < 2:
        return False, "Invalid repository format"
    
    owner, repo_name = parts[0], parts[1]
    
    # Check if repository exists
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return True, "Repository exists"
        elif response.status_code == 404:
            return False, "Repository not found"
        else:
            return False, f"GitHub API error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {e}"

def validate_release_exists(repo_url, version):
    """Check if a specific release exists"""
    if not repo_url.startswith("github.com/"):
        return False, "Not a GitHub repository"
    
    parts = repo_url[len("github.com/"):].split("/")
    if len(parts) < 2:
        return False, "Invalid repository format"
    
    owner, repo_name = parts[0], parts[1]
    
    # Check if release exists
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/releases/tags/{version}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return True, "Release exists"
        elif response.status_code == 404:
            return False, "Release not found"
        else:
            return False, f"GitHub API error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {e}"

def validate_tarball_exists(repo_url, version, ip_name):
    """Check if the tarball file exists"""
    if not repo_url.startswith("github.com/"):
        return False, "Not a GitHub repository"
    
    parts = repo_url[len("github.com/"):].split("/")
    if len(parts) < 2:
        return False, "Invalid repository format"
    
    owner, repo_name = parts[0], parts[1]
    
    # Check if tarball exists
    tarball_url = f"https://github.com/{owner}/{repo_name}/releases/download/{ip_name}-{version}/{version}.tar.gz"
    try:
        response = requests.head(tarball_url, timeout=10)
        if response.status_code == 200:
            return True, "Tarball exists"
        elif response.status_code == 404:
            return False, "Tarball not found"
        else:
            return False, f"HTTP error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {e}"

def validate_ip_data(client):
    """Validate all IP data in the database"""
    db = client.get_database()
    ips_collection = db.get_collection("ips")
    
    # Get all IPs
    cursor = ips_collection.find({})
    ips = list(cursor)
    
    print(f"Validating {len(ips)} IPs...")
    print("=" * 80)
    
    valid_ips = []
    invalid_ips = []
    
    for ip_doc in ips:
        ip_name = ip_doc.get("_id")
        repo_url = ip_doc.get("repo", "")
        releases = ip_doc.get("releases", {})
        
        print(f"\n🔍 Validating: {ip_name}")
        print(f"   Repository: {repo_url}")
        
        # Check repository
        repo_valid, repo_message = validate_github_repository(repo_url)
        print(f"   Repository Status: {'✅' if repo_valid else '❌'} {repo_message}")
        
        if not repo_valid:
            invalid_ips.append({
                'name': ip_name,
                'repo': repo_url,
                'issue': 'Repository not found',
                'message': repo_message
            })
            continue
        
        # Check releases
        valid_releases = []
        invalid_releases = []
        
        for version, release_info in releases.items():
            print(f"   📦 Release {version}:")
            
            # Check if release exists
            release_valid, release_message = validate_release_exists(repo_url, version)
            print(f"      Release: {'✅' if release_valid else '❌'} {release_message}")
            
            # Check if tarball exists
            tarball_valid, tarball_message = validate_tarball_exists(repo_url, version, ip_name)
            print(f"      Tarball: {'✅' if tarball_valid else '❌'} {tarball_message}")
            
            if release_valid and tarball_valid:
                valid_releases.append(version)
            else:
                invalid_releases.append({
                    'version': version,
                    'release_issue': release_message,
                    'tarball_issue': tarball_message
                })
        
        # Categorize IP
        if valid_releases:
            valid_ips.append({
                'name': ip_name,
                'repo': repo_url,
                'valid_releases': valid_releases,
                'invalid_releases': invalid_releases
            })
        else:
            invalid_ips.append({
                'name': ip_name,
                'repo': repo_url,
                'issue': 'No valid releases',
                'releases': invalid_releases
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"\n✅ VALID IPs ({len(valid_ips)}):")
    for ip in valid_ips:
        print(f"   {ip['name']}: {ip['repo']}")
        print(f"      Valid releases: {', '.join(ip['valid_releases'])}")
        if ip['invalid_releases']:
            print(f"      Invalid releases: {len(ip['invalid_releases'])}")
    
    print(f"\n❌ INVALID IPs ({len(invalid_ips)}):")
    for ip in invalid_ips:
        print(f"   {ip['name']}: {ip['repo']}")
        print(f"      Issue: {ip['issue']}")
        if 'releases' in ip:
            for release in ip['releases']:
                print(f"         {release['version']}: {release['release_issue']} / {release['tarball_issue']}")
    
    # Save detailed report
    report = {
        'summary': {
            'total_ips': len(ips),
            'valid_ips': len(valid_ips),
            'invalid_ips': len(invalid_ips)
        },
        'valid_ips': valid_ips,
        'invalid_ips': invalid_ips
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Detailed report saved to: validation_report.json")
    
    return valid_ips, invalid_ips

def main():
    """Main validation function"""
    print("IPM Data Validation Script")
    print("=" * 40)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    
    # Validate the data
    valid_ips, invalid_ips = validate_ip_data(client)
    
    # Close the MongoDB connection
    client.close()
    print("MongoDB connection closed.")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if invalid_ips:
        print("1. Review and fix invalid IPs before using them in production")
        print("2. Consider removing IPs with non-existent repositories")
        print("3. Update release versions to match actual GitHub releases")
    else:
        print("1. All IPs are valid! Your data is in excellent shape.")
    
    print("2. Run this validation script periodically to maintain data quality")
    print("3. Use the validation report to prioritize data cleanup efforts")

if __name__ == "__main__":
    main()
