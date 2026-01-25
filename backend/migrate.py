#!/usr/bin/env python3
"""
Data migration script to transfer IP data from verified_IPs.json to MongoDB.
This script reads the original JSON file and inserts each IP into the MongoDB database.
"""

import json
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

def load_verified_ips(json_file_path):
    """Load the verified_IPs.json file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {json_file_path}")
        print("Please ensure the verified_IPs.json file is in the backend directory.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file_path}: {e}")
        sys.exit(1)

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

def migrate_data(client, verified_ips_data):
    """Migrate the IP data to MongoDB"""
    db = client.get_database()
    ips_collection = db.get_collection("ips")
    
    # Clear existing data (optional - comment out if you want to preserve existing data)
    # ips_collection.delete_many({})
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Starting migration of {len(verified_ips_data)} IPs...")
    
    for ip_name, ip_data in verified_ips_data.items():
        try:
            # Transform the data structure
            # The IP name becomes the _id field
            transformed_ip = {
                "_id": ip_name,
                "description": ip_data.get("description", ""),
                "repo": ip_data.get("repo", ""),
                "author": ip_data.get("author", ""),
                "email": ip_data.get("email", ""),
                "owner": ip_data.get("owner", ""),
                "category": ip_data.get("category", ""),
                "technology": ip_data.get("technology", ""),
                "license": ip_data.get("license", ""),
                "tags": ip_data.get("tags", []),
                "releases": ip_data.get("release", {})  # Note: 'release' in JSON becomes 'releases' in our model
            }
            
            # Insert the IP document
            try:
                ips_collection.insert_one(transformed_ip)
                migrated_count += 1
                print(f"✓ Migrated: {ip_name}")
            except DuplicateKeyError:
                # Update existing document if it already exists
                ips_collection.replace_one({"_id": ip_name}, transformed_ip)
                skipped_count += 1
                print(f"↻ Updated: {ip_name}")
                
        except Exception as e:
            error_count += 1
            print(f"✗ Error migrating {ip_name}: {e}")
    
    print(f"\nMigration completed!")
    print(f"✓ Successfully migrated: {migrated_count} IPs")
    print(f"↻ Updated existing: {skipped_count} IPs")
    print(f"✗ Errors: {error_count} IPs")
    
    if error_count == 0:
        print("🎉 All IPs migrated successfully!")
    else:
        print(f"⚠️  {error_count} IPs had errors during migration.")

def main():
    """Main migration function"""
    print("IPM Data Migration Script")
    print("=" * 40)
    
    # Get the path to verified_IPs.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "verified_IPs.json")
    
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        print(f"Error: {json_file_path} not found.")
        print("Please copy verified_IPs.json to the backend directory before running this script.")
        sys.exit(1)
    
    # Load the verified IPs data
    print(f"Loading data from {json_file_path}...")
    verified_ips_data = load_verified_ips(json_file_path)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    
    # Perform the migration
    migrate_data(client, verified_ips_data)
    
    # Close the MongoDB connection
    client.close()
    print("MongoDB connection closed.")

if __name__ == "__main__":
    main()
