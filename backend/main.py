from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

# Load environment variables
load_dotenv()

app = FastAPI(title="IPM Backend API", version="1.0.0")

# Database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ipm")
client: MongoClient = MongoClient(MONGO_URI)
db: Database = client.get_database()
ips_collection: Collection = db.get_collection("ips")

# Pydantic Models
class Release(BaseModel):
    date: str
    maturity: str
    bus: List[str]
    type: str
    width: str
    height: str
    cell_count: str
    clock_freq_mhz: str
    supply_voltage: List[str]
    draft: bool = False
    sha256: str

class IP(BaseModel):
    name: str = Field(..., alias="_id")
    description: str
    repo: str
    author: str
    email: str
    owner: str
    category: str
    technology: str
    license: str
    tags: List[str]
    releases: Dict[str, Release]

    class Config:
        allow_population_by_field_name = True

class DownloadResponse(BaseModel):
    url: str
    sha256: str

@app.get("/")
async def root():
    return {"message": "IPM Backend API"}

@app.get("/api/v1/ips")
async def list_ips(
    category: Optional[str] = Query(None, description="Filter by category"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    include_drafts: bool = Query(False, description="Include draft releases")
):
    """List all IPs with optional filtering"""
    try:
        # Build filter based on query parameters
        filter_query = {}
        if category:
            filter_query["category"] = category
        if technology:
            filter_query["technology"] = technology
        
        # Get all IPs matching the filter
        cursor = ips_collection.find(filter_query)
        ips = []
        
        for ip_doc in cursor:
            ip_data = dict(ip_doc)
            releases = ip_data.get("releases", {})
            
            # Filter out draft releases if include_drafts is False
            if not include_drafts:
                filtered_releases = {
                    version: release_info
                    for version, release_info in releases.items()
                    if not release_info.get("draft", False)
                }
                # Only include IPs that have at least one non-draft release
                if filtered_releases:
                    ip_data["releases"] = filtered_releases
                    ips.append(ip_data)
            else:
                ips.append(ip_data)
        
        return {"ips": ips, "count": len(ips)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/ips/{ip_name}")
async def get_ip_details(
    ip_name: str,
    include_drafts: bool = Query(False, description="Include draft releases")
):
    """Get details for a specific IP"""
    try:
        ip_doc = ips_collection.find_one({"_id": ip_name})
        if not ip_doc:
            raise HTTPException(status_code=404, detail=f"IP '{ip_name}' not found")
        
        ip_data = dict(ip_doc)
        releases = ip_data.get("releases", {})
        
        # Filter out draft releases if include_drafts is False
        if not include_drafts:
            filtered_releases = {
                version: release_info
                for version, release_info in releases.items()
                if not release_info.get("draft", False)
            }
            ip_data["releases"] = filtered_releases
        
        return ip_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/ips/{ip_name}/{version}/download")
async def download_ip(ip_name: str, version: str):
    """Get download URL for a specific IP version"""
    try:
        ip_doc = ips_collection.find_one({"_id": ip_name})
        if not ip_doc:
            raise HTTPException(status_code=404, detail=f"IP '{ip_name}' not found")
        
        releases = ip_doc.get("releases", {})
        
        # Handle "latest" version
        if version == "latest":
            # Find the most recent non-draft release
            non_draft_versions = [
                v for v, info in releases.items() 
                if not info.get("draft", False)
            ]
            if not non_draft_versions:
                raise HTTPException(status_code=404, detail=f"No non-draft releases found for IP '{ip_name}'")
            # Sort versions and get the latest
            non_draft_versions.sort()
            version = non_draft_versions[-1]
        
        if version not in releases:
            raise HTTPException(status_code=404, detail=f"Version '{version}' not found for IP '{ip_name}'")
        
        release_info = releases[version]
        repo = ip_doc["repo"]
        
        # Parse repo field (format: github.com/owner/repo)
        if repo.startswith("github.com/"):
            repo_parts = repo[len("github.com/"):].split("/")
            if len(repo_parts) >= 2:
                owner, repo_name = repo_parts[0], repo_parts[1]
                
                # Construct GitHub download URL
                download_url = f"https://github.com/{owner}/{repo_name}/releases/download/{ip_name}-{version}/{version}.tar.gz"
                
                return DownloadResponse(
                    url=download_url,
                    sha256=release_info.get("sha256", "")
                )
            else:
                raise HTTPException(status_code=500, detail="Invalid repo format")
        else:
            raise HTTPException(status_code=500, detail="Only GitHub repositories are supported")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing download request: {str(e)}")

# Stub endpoints for future authentication implementation
@app.post("/api/v1/ips")
async def create_ip():
    return {"message": "Not Implemented"}

@app.put("/api/v1/ips/{ip_name}")
async def update_ip(ip_name: str):
    return {"message": "Not Implemented"}

@app.delete("/api/v1/ips/{ip_name}")
async def delete_ip(ip_name: str):
    return {"message": "Not Implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
