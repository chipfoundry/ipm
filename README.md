# IPM Platform

A monorepo containing the IP Management (IPM) platform with a client-server architecture.

## Project Structure

```
ipm-platform/
├── backend/         # FastAPI backend service
│   ├── main.py     # Main FastAPI application
│   ├── migrate.py  # Data migration script
│   ├── requirements.txt
│   └── README.md
├── cli/             # CLI client tool
│   ├── ipm/        # CLI implementation
│   ├── pyproject.toml
│   ├── README.md
│   └── ... (other CLI files)
└── .env             # Environment configuration
```

## Architecture Overview

This project has been refactored from a single CLI tool using local JSON files to a client-server architecture:

- **Backend**: FastAPI service with MongoDB database for IP management
- **CLI Client**: Refactored command-line tool that communicates with the backend API
- **Data Migration**: Script to transfer existing data from JSON to MongoDB

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python migrate.py  # Populate database
python main.py     # Start backend service
```

The backend will be available at `http://127.0.0.1:8000`

### 2. CLI Usage

```bash
cd cli
pip install -e .  # Install CLI in development mode
ipm ls-remote     # List available IPs
ipm install <ip>  # Install an IP
```

## Features

- **IP Management**: Store and retrieve IP package information
- **Release Management**: Handle different versions and releases
- **Filtering**: Filter IPs by category, technology, and draft status
- **Download Management**: Generate direct download URLs for releases
- **CLI Interface**: Command-line tool for IP operations

## Development

- Backend: FastAPI + MongoDB
- CLI: Python + Click + Rich
- Data: Migrated from verified_IPs.json

## API Documentation

Once the backend is running, visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Migration

The `backend/migrate.py` script transfers data from the original `verified_IPs.json` file to MongoDB, maintaining backward compatibility while enabling the new architecture.
