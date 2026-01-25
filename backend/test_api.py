#!/usr/bin/env python3
"""
Simple test script to verify the backend API is working correctly.
Run this after starting the backend service.
"""

import requests
import json
import sys

def test_api():
    """Test the backend API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing IPM Backend API")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Root endpoint working")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is the service running?")
        return False
    
    # Test list IPs endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/ips")
        if response.status_code == 200:
            data = response.json()
            ip_count = data.get("count", 0)
            print(f"✓ List IPs endpoint working - {ip_count} IPs found")
        else:
            print(f"✗ List IPs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ List IPs endpoint error: {e}")
    
    # Test specific IP endpoint (using first available IP)
    try:
        response = requests.get(f"{base_url}/api/v1/ips")
        if response.status_code == 200:
            data = response.json()
            ips = data.get("ips", [])
            if ips:
                first_ip = ips[0]
                ip_name = first_ip.get("_id") or first_ip.get("name")
                
                response2 = requests.get(f"{base_url}/api/v1/ips/{ip_name}")
                if response2.status_code == 200:
                    print(f"✓ Get IP details endpoint working for {ip_name}")
                else:
                    print(f"✗ Get IP details endpoint failed: {response2.status_code}")
            else:
                print("⚠ No IPs found to test with")
        else:
            print("⚠ Cannot test IP details endpoint - list IPs failed")
    except Exception as e:
        print(f"✗ Get IP details endpoint error: {e}")
    
    # Test download endpoint (using first available IP and version)
    try:
        response = requests.get(f"{base_url}/api/v1/ips")
        if response.status_code == 200:
            data = response.json()
            ips = data.get("ips", [])
            if ips:
                first_ip = ips[0]
                ip_name = first_ip.get("_id") or first_ip.get("name")
                releases = first_ip.get("releases", {})
                
                if releases:
                    first_version = list(releases.keys())[0]
                    response2 = requests.get(f"{base_url}/api/v1/ips/{ip_name}/{first_version}/download")
                    if response2.status_code == 200:
                        download_data = response2.json()
                        url = download_data.get("url", "")
                        sha256 = download_data.get("sha256", "")
                        print(f"✓ Download endpoint working for {ip_name}@{first_version}")
                        print(f"  URL: {url}")
                        print(f"  SHA256: {sha256}")
                    else:
                        print(f"✗ Download endpoint failed: {response2.status_code}")
                else:
                    print("⚠ No releases found to test download endpoint")
            else:
                print("⚠ No IPs found to test download endpoint")
        else:
            print("⚠ Cannot test download endpoint - list IPs failed")
    except Exception as e:
        print(f"✗ Download endpoint error: {e}")
    
    print("\n" + "=" * 40)
    print("API test completed!")
    return True

if __name__ == "__main__":
    test_api()
