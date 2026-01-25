#!/bin/bash

echo "Starting IPM Backend Service..."
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import fastapi, uvicorn, pymongo, dotenv" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "Creating .env file with default MongoDB URI..."
    echo "MONGO_URI=mongodb://localhost:27017/ipm" > ../.env
    echo "Please edit ../.env if you need a different MongoDB connection string"
fi

# Check if MongoDB is accessible
echo "Checking MongoDB connection..."
if ! python3 -c "
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('../.env')
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ipm')

try:
    client = MongoClient(mongo_uri)
    client.admin.command('ping')
    print('MongoDB connection successful')
    client.close()
except Exception as e:
    print(f'MongoDB connection failed: {e}')
    print('Please ensure MongoDB is running and accessible')
    exit(1)
" 2>/dev/null; then
    echo "MongoDB connection failed. Please check your MongoDB setup."
    exit 1
fi

# Check if data migration is needed
echo "Checking if data migration is needed..."
if python3 -c "
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('../.env')
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ipm')

client = MongoClient(mongo_uri)
db = client.get_database()
ips_collection = db.get_collection('ips')

if ips_collection.count_documents({}) == 0:
    print('Database is empty. Running migration...')
    exit(1)
else:
    print('Database already contains data')
    exit(0)
" 2>/dev/null; then
    echo "Database is ready"
else
    echo "Running data migration..."
    python3 migrate.py
fi

echo "Starting FastAPI service..."
echo "Service will be available at: http://127.0.0.1:8000"
echo "API documentation: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop the service"
echo "================================"

# Start the service
python3 main.py
