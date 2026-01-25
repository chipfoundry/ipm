# IPM Backend Service

This is the FastAPI backend service for the IPM (IP Management) platform. It provides a REST API for managing IP packages and their releases.

## Features

- **IP Management**: Store and retrieve IP package information
- **Release Management**: Handle different versions and releases of IPs
- **Filtering**: Support for filtering IPs by category, technology, and draft status
- **Download URLs**: Generate direct download URLs for IP releases
- **MongoDB Integration**: Persistent storage using MongoDB

## API Endpoints

### GET /api/v1/ips
List all IPs with optional filtering:
- `category`: Filter by IP category (e.g., "digital", "analog", "memory")
- `technology`: Filter by technology (e.g., "sky130", "gf180mcuC")
- `include_drafts`: Include draft releases (default: false)

### GET /api/v1/ips/{ip_name}
Get details for a specific IP:
- `include_drafts`: Include draft releases (default: false)

### GET /api/v1/ips/{ip_name}/{version}/download
Get download information for a specific IP version:
- Returns download URL and SHA256 hash
- Supports "latest" version to get the most recent non-draft release

## Setup

### Prerequisites
- Python 3.8+
- MongoDB running locally or accessible via connection string

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your MongoDB connection string:
```
MONGO_URI=mongodb://localhost:27017/ipm
```

3. Run the migration script to populate the database:
```bash
python migrate.py
```

4. Start the backend service:
```bash
python main.py
```

The service will be available at `http://127.0.0.1:8000`

## Data Migration

The `migrate.py` script transfers data from the original `verified_IPs.json` file to MongoDB. It:

- Connects to MongoDB using the `MONGO_URI` from `.env`
- Reads the JSON file and transforms the data structure
- Inserts each IP into the `ips` collection
- Uses the IP name as the document `_id` field
- Transforms `release` field to `releases` for consistency

## Development

### Running with Uvicorn
For development, you can also run the service using uvicorn directly:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### API Documentation
Once running, visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Data Models

### Release
- `date`: Release date
- `maturity`: Maturity level
- `bus`: List of supported bus interfaces
- `type`: IP type (soft/hard)
- `width`: Physical width
- `height`: Physical height
- `cell_count`: Number of cells
- `clock_freq_mhz`: Clock frequency
- `supply_voltage`: List of supply voltages
- `draft`: Whether this is a draft release
- `sha256`: SHA256 hash of the release tarball

### IP
- `name`: IP name (stored as `_id`)
- `description`: IP description
- `repo`: Repository URL (format: github.com/owner/repo)
- `author`: IP author
- `email`: Contact email
- `owner`: IP owner
- `category`: IP category
- `technology`: Technology node
- `license`: License information
- `tags`: List of tags
- `releases`: Dictionary of releases by version
