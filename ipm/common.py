#!/usr/bin/env python3
# Copyright 2022 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import json
import requests
import shutil
import tarfile
from datetime import datetime
from typing import Callable

import rich
from rich.table import Table
import click

# Datetime Helpers
ISO8601_FMT = "%Y-%m-%dT%H:%M:%SZ"


def date_to_iso8601(date: datetime) -> str:
    return date.strftime(ISO8601_FMT)


def date_from_iso8601(string: str) -> datetime:
    return datetime.strptime(string, ISO8601_FMT)


# ---

IPM_REPO_OWNER = os.getenv("IPM_REPO_OWNER") or "efabless"
IPM_REPO_NAME = os.getenv("IPM_REPO_NAME") or "ipm"
IPM_REPO_ID = f"{IPM_REPO_OWNER}/{IPM_REPO_NAME}"
IPM_REPO_HTTPS = f"https://github.com/{IPM_REPO_ID}"
IPM_REPO_API = f"https://api.github.com/repos/{IPM_REPO_ID}"
IPM_DEFAULT_HOME = os.path.join(os.path.expanduser("~"), ".ipm")
# Default IP installation path with environment variable override
IP_DEFAULT_ROOT = os.getenv("IP_ROOT") or os.path.join(os.path.expanduser("~"), ".ipm")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub Personal Access Token

LOCAL_JSON_FILE_NAME = "Installed_IPs.json"
DEPENDENCIES_FILE_NAME = "dependencies.json"
REMOTE_JSON_FILE_NAME = (
    "https://raw.githubusercontent.com/chipfoundry/ipm/refs/heads/main/ip-catalog-platform.json"
)

class LocalIP:
    def __init__(self, ip, ipm_iproot):
        self.ip = ip
        self.ipm_iproot = ipm_iproot

    def init_info(self, ip_root, technology="sky130", version=None):
        self.ip_root = ip_root
        local_json_file = os.path.join(self.ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(local_json_file) as json_file:
            data = json.load(json_file)
        for key, values in data.items():
            for value in values:
                if value["name"] == self.ip and value["technology"] == technology:
                    self.name = self.ip
                    self.repo = value["repo"]
                    self.version = value["version"]
                    self.date = value["date"]
                    self.author = value["author"]
                    self.email = value["email"]
                    self.category = key
                    self.type = value["type"]
                    self.status = value["status"]
                    self.width = value["width"]
                    self.height = value["height"]
                    self.technology = technology
                    self.tag = value["tag"]
                    self.cell_count = value["cell_count"]
                    self.clk_freq = value["clk_freq"]
                    self.license = value["license"]
        release_url = f"https://{self.repo}/releases/download/{self.version}/{self.version}.tar.gz"
        self.release_url = release_url

    def get_info(self, technology="sky130", version=None):
        local_json_file = os.path.join(self.ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(local_json_file) as json_file:
            data = json.load(json_file)
        for key, values in data.items():
            for value in values:
                if value["name"] == self.ip and value["technology"] == technology:
                    self.name = self.ip
                    self.repo = value["repo"]
                    self.version = value["version"]
                    self.date = value["date"]
                    self.author = value["author"]
                    self.email = value["email"]
                    self.category = key
                    self.type = value["type"]
                    self.status = value["status"]
                    self.width = value["width"]
                    self.height = value["height"]
                    self.technology = technology
                    self.tag = value["tag"]
                    self.cell_count = value["cell_count"]
                    self.clk_freq = value["clk_freq"]
                    self.license = value["license"]
                    self.ip_root = value["ip_root"]
        release_url = f"https://{self.repo}/releases/download/{self.version}/{self.version}.tar.gz"
        self.release_url = release_url

    def get_info_from_atr(self, ip_info):
        ip_info_dict = {}
        for attribute in ip_info.__dict__:
            ip_info_dict[attribute] = getattr(ip_info, attribute)
        return ip_info_dict

    def add_ip_to_json(self, ip_info, ip_root):
        local_json_file = os.path.join(self.ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(local_json_file) as json_file:
            json_decoded = json.load(json_file)
        ip_info_dict = self.get_info_from_atr(ip_info)
        del ip_info_dict["release"]
        self.ip_root = os.path.abspath(ip_root)
        ip_info_dict["ip_root"] = self.ip_root

        json_decoded[ip_info_dict["category"]].append(ip_info_dict)

        with open(local_json_file, "w") as json_file:
            json.dump(json_decoded, json_file)

    def remove_ip_from_json(self):
        json_file = os.path.join(self.ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(json_file, 'r') as f:
            json_decoded = json.load(f)
        self.get_info()
        ip_info_dict = self.get_info_from_atr(self)
        ip_category = json_decoded[ip_info_dict["category"]]

        for ips in ip_category:
            if ips['name'] == ip_info_dict['name'] and ips['ip_root'] == self.ip_root:
                ip_category.remove(ips)
        json_decoded[ip_info_dict["category"]] = ip_category

        with open(json_file, "w") as json_file:
            json.dump(json_decoded, json_file)

    def remove_from_deps(self, deps_file):
        if deps_file:
            json_file = os.path.join(deps_file, DEPENDENCIES_FILE_NAME)
        else:
            json_file = os.path.join(self.ip_root, DEPENDENCIES_FILE_NAME)

        with open(json_file, 'r') as f:
            json_decoded = json.load(f)
        ip_info_dict = self.get_info_from_atr(self)
        ip_category = json_decoded["IP"]
        for ips in ip_category:
            if ips['name'] == ip_info_dict['name']:
                ip_category.remove(ips)
        json_decoded["IP"] = ip_category

        with open(json_file, "w") as json_file:
            json.dump(json_decoded, json_file)

    def create_deps(self, ip_info, deps_file):
        if deps_file:
            local_json_file = os.path.join(deps_file, DEPENDENCIES_FILE_NAME)
        else:
            local_json_file = os.path.join(self.ip_root, DEPENDENCIES_FILE_NAME)

        if os.path.exists(local_json_file):
            with open(local_json_file) as json_file:
                json_decoded = json.load(json_file)
        else:
            json_decoded = {
                "IP": []
            }
        ip_info_dict = self.get_info_from_atr(ip_info)
        tmp_dict = {
            "name": ip_info_dict["name"],
            "version": ip_info_dict["version"],
            "technology": ip_info_dict["technology"]
        }
        json_decoded['IP'].append(tmp_dict)

        with open(local_json_file, "w") as json_file:
            json.dump(json_decoded, json_file)

class RemoteIP:
    def __init__(self, ip):
        self.ip = ip

    def get_info(self, technology="sky130", version=None):
        resp = requests.get(REMOTE_JSON_FILE_NAME)
        data = json.loads(resp.text)
        
        # Check if JSON is in the new format (ip-catalog-platform.json)
        if self.ip in data:
            # New format - IPs are indexed by name directly
            value = data[self.ip]
            self.name = self.ip
            self.repo = value["repo"]
            self.author = value["author"]
            self.email = value["email"]
            self.category = value["category"]
            self.technology = technology
            self.license = value["license"]
            self.tag = value["tags"]
            
            # Extract release information
            self.release = value["release"]
            
            # If version is not specified, use the latest
            if version is None:
                # Find the latest version by comparing version strings
                versions = list(value["release"].keys())
                if versions:
                    latest_version = versions[-1]  # Assume last version in the list is latest
                    self.version = latest_version
                    release_info = value["release"][latest_version]
                    self.date = release_info["date"]
                    self.type = release_info["type"]
                    self.width = release_info["width"]
                    self.height = release_info["height"]
                    self.cell_count = release_info["cell_count"]
                    self.clk_freq = release_info["clock_freq_mhz"]
                    self.status = release_info.get("maturity", "unknown")
            else:
                # Use specified version if available
                if version in value["release"]:
                    self.version = version
                    release_info = value["release"][version]
                    self.date = release_info["date"]
                    self.type = release_info["type"]
                    self.width = release_info["width"]
                    self.height = release_info["height"]
                    self.cell_count = release_info["cell_count"]
                    self.clk_freq = release_info["clock_freq_mhz"]
                    self.status = release_info.get("maturity", "unknown")
        else:
            # Original format - iterate through categories
            for key, values in data.items():
                for value in values:
                    if value["name"] == self.ip and value["technology"] == technology:
                        self.name = self.ip
                        self.repo = value["repo"]
                        self.release = value["release"]
                        if version is None:
                            self.version = value["release"][-1]["version"]
                            self.date = value["release"][-1]["date"]
                        else:
                            for v in value["release"]:
                                if v["version"] == version:
                                    self.version = v["version"]
                                    self.date = v["date"]
                        self.author = value["author"]
                        self.email = value["email"]
                        self.category = key
                        self.type = value["type"]
                        self.status = value["status"]
                        self.width = value["width"]
                        self.height = value["height"]
                        self.technology = technology
                        self.tag = value["tag"]
                        self.cell_count = value["cell_count"]
                        self.clk_freq = value["clk_freq"]
                        self.license = value["license"]
        
        # Use only the specific GitHub format mentioned
        self.possible_urls = []
        
        # Get repo parts to construct the URL correctly
        repo_parts = self.repo.split('/')
        if len(repo_parts) >= 3 and "github.com" in self.repo:  # GitHub format
            repo_name = repo_parts[-1]  # Extract repo name (e.g., EF_AES)
            # Use only this specific URL format: https://github.com/chipfoundry/EF_AES/archive/refs/tags/EF_AES-v1.1.0.tar.gz
            self.possible_urls.append(f"https://{self.repo}/archive/refs/tags/{repo_name}-{self.version}.tar.gz")
        else:
            # Fallback to standard format for non-GitHub repos
            self.possible_urls.append(f"https://{self.repo}/releases/download/{self.version}/{self.version}.tar.gz")
            
        # We'll set the first URL as the default
        self.release_url = self.possible_urls[0]
        print(f"Debug - Release URL: {self.release_url}")


def opt_ipm_iproot(function: Callable):
    function = click.option(
        "--ipm-iproot",
        required=False,
        default=os.getenv("IPM_IPROOT") or IPM_DEFAULT_HOME,
        help="Path to the IPM root where the IPs will reside",
        show_default=True,
    )(function)
    return function

def checkdir(path):
    return os.path.isdir(path)

def create_local_JSON(file_path):
    dictionary = {
        "analog": [],
        "comm": [],
        "dataconv": [],
        "digital": [],
        "technolgy": [],
    }
    with open(file_path, "w") as outfile:
        json.dump(dictionary, outfile)


def check_ipm_directory(console: rich.console.Console, ipm_iproot) -> bool:
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    JSON_FILE_PATH = os.path.join(IPM_DIR_PATH, LOCAL_JSON_FILE_NAME)

    if ipm_iproot == IPM_DEFAULT_HOME:
        if not os.path.exists(ipm_iproot):
            os.mkdir(ipm_iproot)
            create_local_JSON(JSON_FILE_PATH)
        else:  # .ipm folder exists
            if not os.path.exists(IPM_DIR_PATH):
                os.mkdir(IPM_DIR_PATH)
                create_local_JSON(JSON_FILE_PATH)
            else:  # .ipm/ipm folder exists
                if not os.path.exists(JSON_FILE_PATH):
                    create_local_JSON(JSON_FILE_PATH)
    else:
        if not os.path.exists(ipm_iproot):
            console.print(
                "[red]The IPM_IPROOT does not exist, please specify a correct IPM_IPROOT to continue"
            )
            return False
        else:
            if not os.path.exists(IPM_DIR_PATH):
                os.mkdir(IPM_DIR_PATH)
                create_local_JSON(JSON_FILE_PATH)
            else:  # <ipm_iproot>/ipm folder exists
                if not os.path.exists(JSON_FILE_PATH):
                    create_local_JSON(JSON_FILE_PATH)
    return True

def check_ip_root_dir(console: rich.console.Console, ip_root) -> bool:
    if not os.path.isdir(ip_root):
        # Create the directory if it doesn't exist
        try:
            console.print(f"[yellow]The IP root directory {ip_root} doesn't exist. Creating it...")
            os.makedirs(ip_root, exist_ok=True)
            return True
        except Exception as e:
            console.print(f"[red]Error creating ip-root directory {ip_root}: {str(e)}")
            return False
    else:
        return True


def list_IPs(console: rich.console.Console, ipm_iproot, remote, category="all"):
    if remote:
        resp = requests.get(REMOTE_JSON_FILE_NAME)
        data = json.loads(resp.text)
    else:
        JSON_FILE = os.path.join(ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(JSON_FILE) as json_file:
            data = json.load(json_file)

    table = Table()

    table.add_column("Category", style="cyan")
    table.add_column("IP Name", style="magenta")
    table.add_column("Version")
    table.add_column("Author")
    # table.add_column("Date")
    table.add_column("Type")
    table.add_column("Tag")
    # table.add_column("Cell count")
    # table.add_column("Clk freq (MHz)")
    table.add_column("Status")
    # table.add_column("Width (um)")
    # table.add_column("Height (um)")
    table.add_column("Technology", style="cyan")
    table.add_column("License", style="magenta")

    total_IPs = 0
    
    # Check if we're dealing with the new format (ip-catalog-platform.json)
    # by looking at the structure - in the new format, IPs are indexed by name directly
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data[first_key]:
        # New format IP catalog
        ip_list = []
        
        for ip_name, ip_data in data.items():
            # Skip if category filter is applied and doesn't match
            if category != "all" and ip_data["category"] != category:
                continue
                
            # Get the latest version
            if ip_data["release"]:
                versions = list(ip_data["release"].keys())
                latest_version = versions[-1]  # Assume last one is latest
                latest_release = ip_data["release"][latest_version]
                
                table.add_row(
                    ip_data["category"],
                    ip_name,
                    latest_version,
                    ip_data["author"],
                    # latest_release["date"],
                    latest_release["type"],
                    ",".join(ip_data["tags"]),
                    # latest_release["cell_count"],
                    # latest_release["clock_freq_mhz"],
                    latest_release.get("maturity", "unknown"),
                    # latest_release["width"],
                    # latest_release["height"],
                    ip_data["technology"],
                    ip_data["license"],
                )
                total_IPs += 1
        
        if total_IPs > 0:
            console.print(table)
            console.print(f"Total {total_IPs} IP(s)")
        else:
            console.print("[red]No IPs Found")
            
    else:
        # Original format IP catalog
        if category == "all":
            for key, values in data.items():
                for value in values:
                    table.add_row(
                        key,
                        value["name"],
                        value["release"][-1]["version"],
                        value["author"],
                        # value["release"][-1]["date"],
                        value["type"],
                        ",".join(value["tag"]),
                        # value["cell_count"],
                        # value["clk_freq"],
                        value["status"],
                        # value["width"],
                        # value["height"],
                        value["technology"],
                        value["license"],
                    )
                total_IPs = total_IPs + len(values)
            if total_IPs > 0:
                console.print(table)
                console.print(f"Total {total_IPs} IP(s)")
            else:
                console.print("[red]No IPs Found")
        else:
            for value in data[category]:
                table.add_row(
                    category,
                    value["name"],
                    value["release"][-1]["version"],
                    value["author"],
                    # value["release"][-1]["date"],
                    value["type"],
                    ",".join(value["tag"]),
                    # value["cell_count"],
                    # value["clk_freq"],
                    value["status"],
                    # value["width"],
                    # value["height"],
                    value["technology"],
                    value["license"],
                )
            total_IPs = total_IPs + len(data[category])
            if total_IPs > 0:
                console.print(table)
                console.print(f"Total {total_IPs} IP(s)")
            else:
                console.print("[red]No IPs Found")


def list_IPs_local(console: rich.console.Console, ipm_iproot, remote, category="all", ip_root=None):
    # Use the environment-aware default if ip_root is None
    if ip_root is None:
        ip_root = IP_DEFAULT_ROOT
        
    if remote:
        resp = requests.get(REMOTE_JSON_FILE_NAME)
        data = json.loads(resp.text)
    else:
        JSON_FILE = os.path.join(ipm_iproot, LOCAL_JSON_FILE_NAME)
        with open(JSON_FILE) as json_file:
            data = json.load(json_file)

    table = Table()

    table.add_column("Category", style="cyan")
    table.add_column("IP Name", style="magenta")
    table.add_column("Version")
    table.add_column("Author")
    # table.add_column("Date")
    table.add_column("Type")
    table.add_column("Tag")
    # table.add_column("Cell count")
    # table.add_column("Clk freq (MHz)")
    table.add_column("Status")
    # table.add_column("Width (um)")
    # table.add_column("Height (um)")
    table.add_column("Technology", style="cyan")
    table.add_column("License", style="magenta")
    table.add_column("IP path")

    total_IPs = 0
    
    # Check if we're dealing with the new format (ip-catalog-platform.json)
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data[first_key]:
        # New format IP catalog
        for ip_name, ip_data in data.items():
            # Skip if category filter is applied and doesn't match
            if category != "all" and ip_data["category"] != category:
                continue
                
            # Get the latest version
            if ip_data["release"]:
                versions = list(ip_data["release"].keys())
                latest_version = versions[-1]  # Assume last one is latest
                latest_release = ip_data["release"][latest_version]
                
                # For local display we need IP path - use current ip_root if the stored one is missing
                # This handles the case where IPs were installed before IP_ROOT was implemented
                stored_ip_root = ip_data.get("ip_root", ip_root)
                ip_path = os.path.join(stored_ip_root, ip_name)
                
                table.add_row(
                    ip_data["category"],
                    ip_name,
                    latest_version,
                    ip_data["author"],
                    # latest_release["date"],
                    latest_release["type"],
                    ",".join(ip_data["tags"]),
                    # latest_release["cell_count"],
                    # latest_release["clock_freq_mhz"],
                    latest_release.get("maturity", "unknown"),
                    # latest_release["width"],
                    # latest_release["height"],
                    ip_data["technology"],
                    ip_data["license"],
                    ip_path
                )
                total_IPs += 1
        
        if total_IPs > 0:
            console.print(table)
            console.print(f"Total {total_IPs} IP(s)")
        else:
            console.print("[red]No IPs Found")
    else:
        # Original format IP catalog
        if category == "all":
            for key, values in data.items():
                for value in values:
                    # Use stored ip_root or default to current ip_root if missing
                    stored_ip_root = value.get("ip_root", ip_root)
                    ip_path = os.path.join(stored_ip_root, value["name"])
                    
                    table.add_row(
                        key,
                        value["name"],
                        value["version"],
                        value["author"],
                        # value["date"],
                        value["type"],
                        ",".join(value["tag"]),
                        # value["cell_count"],
                        # value["clk_freq"],
                        value["status"],
                        # value["width"],
                        # value["height"],
                        value["technology"],
                        value["license"],
                        ip_path
                    )
                total_IPs = total_IPs + len(values)
            if total_IPs > 0:
                console.print(table)
                console.print(f"Total {total_IPs} IP(s)")
            else:
                console.print("[red]No IPs Found")
        else:
            for value in data[category]:
                # Use stored ip_root or default to current ip_root if missing
                stored_ip_root = value.get("ip_root", ip_root)
                ip_path = os.path.join(stored_ip_root, value["name"])
                
                table.add_row(
                    category,
                    value["name"],
                    value["version"],
                    value["author"],
                    # value["date"],
                    value["type"],
                    ",".join(value["tag"]),
                    # value["cell_count"],
                    # value["clk_freq"],
                    value["status"],
                    # value["width"],
                    # value["height"],
                    value["technology"],
                    value["license"],
                    ip_path
                )
            total_IPs = total_IPs + len(data[category])
            if total_IPs > 0:
                console.print(table)
                console.print(f"Total {total_IPs} IP(s)")
            else:
                console.print("[red]No IPs Found")


# Gets a list of all available IP "names"
def get_IP_list(ipm_iproot, remote):
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    JSON_FILE = ""
    IP_list = []
    if remote:
        resp = requests.get(REMOTE_JSON_FILE_NAME)
        data = json.loads(resp.text)
    else:
        JSON_FILE = os.path.join(IPM_DIR_PATH, LOCAL_JSON_FILE_NAME)
        with open(JSON_FILE) as json_file:
            data = json.load(json_file)
            
    # Check if we're dealing with the new format (ip-catalog-platform.json)
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data[first_key]:
        # New format - IPs are indexed by name directly
        for ip_name in data.keys():
            IP_list.append(ip_name)
    else:
        # Original format - iterate through categories
        for key, values in data.items():
            for value in values:
                IP_list.append(value["name"])
    return IP_list


def get_IP_info(console: rich.console.Console, ipm_iproot, ip, remote):
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    JSON_FILE = ""
    table = Table()
    table.add_column("Category", style="cyan")
    table.add_column("IP Name", style="magenta")
    table.add_column("Version")
    table.add_column("Author")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Tag")
    table.add_column("Cell count")
    table.add_column("Clk freq (MHz)")
    table.add_column("Status")
    table.add_column("Width (um)")
    table.add_column("Height (um)")
    table.add_column("Technology", style="cyan")
    table.add_column("License", style="magenta")
    if remote:
        resp = requests.get(REMOTE_JSON_FILE_NAME)
        data = json.loads(resp.text)
    else:
        JSON_FILE = os.path.join(IPM_DIR_PATH, LOCAL_JSON_FILE_NAME)
        with open(JSON_FILE) as json_file:
            data = json.load(json_file)
            
    # Check if we're dealing with the new format (ip-catalog-platform.json)
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data[first_key]:
        # New format - IPs are indexed by name directly
        if ip in data:
            ip_data = data[ip]
            for version, release in ip_data["release"].items():
                table.add_row(
                    ip_data["category"],
                    ip,
                    version,
                    ip_data["author"],
                    release["date"],
                    release["type"],
                    ",".join(ip_data["tags"]),
                    str(release["cell_count"]),
                    str(release["clock_freq_mhz"]),
                    release.get("maturity", "unknown"),
                    str(release["width"]),
                    str(release["height"]),
                    ip_data["technology"],
                    ip_data["license"],
                )
    else:
        # Original format - iterate through categories
        for key, values in data.items():
            for value in values:
                if value["name"] == ip:
                    for i in range(0, len(value["release"])):
                        table.add_row(
                            key,
                            value["name"],
                            value["release"][i]["version"],
                            value["author"],
                            value["release"][i]["date"],
                            value["type"],
                            ",".join(value["tag"]),
                            value["cell_count"],
                            value["clk_freq"],
                            value["status"],
                            value["width"],
                            value["height"],
                            value["technology"],
                            value["license"],
                        )
    console.print(table)


def install_ip(
    console: rich.console.Console,
    ipm_iproot,
    ip,
    overwrite,
    technology,
    version,
    ip_root,
    deps_file
):
    ip_path = os.path.join(ip_root, ip)
    if os.path.exists(ip_path):
        if len(os.listdir(ip_path)) != 0:
            if not overwrite:
                console.print(
                    f"There already exists a non-empty folder for the IP [green]{ip}",
                    f"at {ip_root}, to overwrite it add the option --overwrite",
                )
                return
            else:
                console.print(f"Removing exisiting IP {ip} at {ip_root}")
                local_ip = LocalIP(ip, ipm_iproot)
                local_ip.remove_ip_from_json()
                local_ip.remove_from_deps(deps_file)
                shutil.rmtree(ip_path)
        else:
            shutil.rmtree(ip_path)

    remote_ip = RemoteIP(ip)
    local_ip = LocalIP(ip, ipm_iproot)
    remote_ip.get_info(technology=technology, version=version)
    console.print(f"[green] IP {ip} is getting installed at {ip_path}")
    
    # Set up headers with authentication if GitHub token is available
    headers = {}
    if GITHUB_TOKEN and "github.com" in remote_ip.repo:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        console.print(f"[green] Using GitHub authentication for {ip}")
    
    # Only try the specified URL format
    console.print(f"[yellow] Downloading from: {remote_ip.release_url}")
    response = requests.get(remote_ip.release_url, stream=True, headers=headers, allow_redirects=True)
    
    if response.status_code != 200:
        console.print(
            f"[red]The IP {ip} version {remote_ip.version} could not be found remotely: HTTP {response.status_code}"
        )
        console.print(f"[red]URL attempted: {remote_ip.release_url}")
        exit(1)
    
    # Download the tarball
    tarball_path = os.path.join(ip_root, f"{ip}.tar.gz")
    with open(tarball_path, "wb") as f:
        f.write(response.content)
    
    # Create a temp directory for extraction
    temp_extract_dir = os.path.join(ip_root, f"{ip}_temp_extract")
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir)
    
    # Extract the tarball to the temp directory
    console.print(f"[green] Extracting tarball from: {remote_ip.release_url}")
    file = tarfile.open(tarball_path)
    file.extractall(temp_extract_dir)
    file.close()
    
    # For GitHub archives, we expect a top-level directory
    extracted_contents = os.listdir(temp_extract_dir)
    
    if len(extracted_contents) == 1 and os.path.isdir(os.path.join(temp_extract_dir, extracted_contents[0])):
        # GitHub format with top-level directory
        github_dir = os.path.join(temp_extract_dir, extracted_contents[0])
        console.print(f"[green] Found GitHub-style archive with root directory: {extracted_contents[0]}")
        
        # Create the IP directory
        os.makedirs(ip_path, exist_ok=True)
        
        # Move contents from GitHub directory to ip_path
        for item in os.listdir(github_dir):
            s = os.path.join(github_dir, item)
            d = os.path.join(ip_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    else:
        # Regular format without top-level directory
        # Move contents from temp directory to ip_path
        console.print(f"[green] Found standard archive format with multiple files at root level")
        os.makedirs(ip_path, exist_ok=True)
        for item in extracted_contents:
            s = os.path.join(temp_extract_dir, item)
            d = os.path.join(ip_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    
    # Clean up temporary files
    shutil.rmtree(temp_extract_dir)
    os.remove(tarball_path)
    
    console.print(
        f"[green]Successfully installed {ip} version {remote_ip.version} to the directory {ip_path}"
    )
    local_ip.add_ip_to_json(remote_ip, ip_root)
    local_ip.create_deps(remote_ip, deps_file)


def install_deps_ip(
    console: rich.console.Console,
    ipm_iproot,
    overwrite,
    ip_root,
    deps_file,
    IP_list
):
    if deps_file:
        JSON_FILE = os.path.join(deps_file, DEPENDENCIES_FILE_NAME)
    else:
        JSON_FILE = os.path.join(ip_root, DEPENDENCIES_FILE_NAME)

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as json_file:
            json_decoded = json.load(json_file)
    else:
        console.print(f"[red]ERROR : {JSON_FILE} couldn't be found")
        exit(1)
    ips = json_decoded['IP']
    for ip_obj in ips:
        ip = ip_obj['name']
        version = ip_obj['version']
        technology = ip_obj['technology']
        if ip not in IP_list:
            print(f"[red]IP {ip} is not a valid IP")
            exit(1)
        ip_path = os.path.join(ip_root, ip)
        if os.path.exists(ip_path):
            if len(os.listdir(ip_path)) != 0:
                if not overwrite:
                    console.print(
                        f"There already exists a non-empty folder for the IP [green]{ip}",
                        f"at {ip_root}, to overwrite it add the option --overwrite",
                    )
                    return
                else:
                    console.print(f"Removing exisiting IP {ip} at {ip_root}")
                    local_ip = LocalIP(ip, ipm_iproot)
                    local_ip.remove_ip_from_json()
                    local_ip.remove_from_deps(deps_file)
                    shutil.rmtree(ip_path)
            else:
                shutil.rmtree(ip_path)
        remote_ip = RemoteIP(ip)
        local_ip = LocalIP(ip, ipm_iproot)
        remote_ip.get_info(technology=technology, version=version)
        
        # Set up headers with authentication if GitHub token is available
        headers = {}
        if GITHUB_TOKEN and "github.com" in remote_ip.repo:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
            console.print(f"[green] Using GitHub authentication for {ip}")
        
        # Only try the specified URL format
        console.print(f"[yellow] Downloading from: {remote_ip.release_url}")
        response = requests.get(remote_ip.release_url, stream=True, headers=headers, allow_redirects=True)
        
        if response.status_code != 200:
            console.print(
                f"[red]The IP {ip} version {remote_ip.version} could not be found remotely: HTTP {response.status_code}"
            )
            console.print(f"[red]URL attempted: {remote_ip.release_url}")
            exit(1)
        
        # Download the tarball
        tarball_path = os.path.join(ip_root, f"{ip}.tar.gz")
        with open(tarball_path, "wb") as f:
            f.write(response.content)
            
        # Create a temp directory for extraction
        temp_extract_dir = os.path.join(ip_root, f"{ip}_temp_extract")
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        os.makedirs(temp_extract_dir)
        
        # Extract the tarball to the temp directory
        console.print(f"[green] Extracting tarball from: {remote_ip.release_url}")
        file = tarfile.open(tarball_path)
        file.extractall(temp_extract_dir)
        file.close()
        
        # For GitHub archives, we expect a top-level directory
        extracted_contents = os.listdir(temp_extract_dir)
        
        if len(extracted_contents) == 1 and os.path.isdir(os.path.join(temp_extract_dir, extracted_contents[0])):
            # GitHub format with top-level directory
            github_dir = os.path.join(temp_extract_dir, extracted_contents[0])
            console.print(f"[green] Found GitHub-style archive with root directory: {extracted_contents[0]}")
            
            # Create the IP directory
            os.makedirs(ip_path, exist_ok=True)
            
            # Move contents from GitHub directory to ip_path
            for item in os.listdir(github_dir):
                s = os.path.join(github_dir, item)
                d = os.path.join(ip_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        else:
            # Regular format without top-level directory
            # Move contents from temp directory to ip_path
            console.print(f"[green] Found standard archive format with multiple files at root level")
            os.makedirs(ip_path, exist_ok=True)
            for item in extracted_contents:
                s = os.path.join(temp_extract_dir, item)
                d = os.path.join(ip_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        
        # Clean up temporary files
        shutil.rmtree(temp_extract_dir)
        os.remove(tarball_path)
        
        console.print(
            f"[green]Successfully installed {ip} version {remote_ip.version} to the directory {ip_path}"
        )
        local_ip.add_ip_to_json(remote_ip, ip_root)


def uninstall_ip(console: rich.console.Console, ipm_iproot, ip, ip_root, deps_file):
    ip_path = os.path.join(ip_root, ip)
    local_ip = LocalIP(ip, ipm_iproot)
    if os.path.exists(ip_path):
        local_ip.remove_ip_from_json()
        local_ip.remove_from_deps(deps_file)
        shutil.rmtree(ip_path, ignore_errors=False, onerror=None)
        console.print(
            f'[green]Successfully uninstalled {ip} version {local_ip.version}'
        )
    else:
        console.print(
            f"The IP {ip} was not found at the directory {ip_root}, you may have removed it manually or renamed the folder"
        )


def check_IP(console, ipm_iproot, ip, update=False, version=None, technology="sky130", ip_root=None):
    update_counter = 0
    # Use the environment-aware default if ip_root is None
    if ip_root is None:
        ip_root = IP_DEFAULT_ROOT
        
    if ip == "all":  # Checks or updates all installed IPs
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if len(IP_list) == 0:  # No installed IPs
            if update:
                console.print("[red]No installed IPs to update")
            else:
                console.print("[red]No installed IPs to check")
        else:  # There are installed IPs
            console.print("Checking all Installed IP(s) for updates")
            for ip in IP_list:  # Loops on all available IPs
                local_ip = LocalIP(ip, ipm_iproot)
                local_ip.get_info(technology=technology, version=version)
                remote_ip = RemoteIP(ip)
                remote_ip.get_info(technology=technology, version=version)
                if version is None:
                    if (
                        local_ip.version
                        == remote_ip.version
                    ):  # IP is up to date
                        console.print(
                            f"[white]The IP [magenta]{ip}"
                            f"[white] is up to date; version {local_ip.version}"
                        )
                    else:
                        if (
                            update
                        ):  # If update flag is True it uninstalls the old version and installs the new one
                            console.print(f"Updating {ip}[white]...")
                            uninstall_ip(console, ipm_iproot, ip, local_ip.ip_root, deps_file=local_ip.ip_root)
                            install_ip(
                                console=console,
                                ipm_iproot=ipm_iproot,
                                ip=ip,
                                overwrite=True,
                                technology=technology,
                                version=remote_ip.version,
                                ip_root=local_ip.ip_root,
                                deps_file=local_ip.ip_root
                            )
                            update_counter = update_counter + 1
                        else:  # If it only needs a check it prints out a message to the user that there is a newer version
                            console.print(
                                f"[yellow]The IP [magenta]{ip}"
                                f"[yellow] has a newer version {remote_ip.version} to update the IP run [white]'ipm update --ip {ip}'"
                            )
                            update_counter = update_counter + 1
            if update_counter > 0:  # There were one or more out dated IP
                if update:
                    console.print(f"[green]Number of updated IP(s): {update_counter}")
                else:
                    console.print(
                        f"[red]There are newer versions for {update_counter} IP(s), to update them all run [white]'ipm update --all' "
                    )
            else:
                console.print("[green]All the installed IP(s) are up to date")

    else:  # Checks or Updates a single IP
        local_ip = LocalIP(ip, ipm_iproot)
        local_ip.get_info(technology=technology, version=version)
        remote_ip = RemoteIP(ip)
        remote_ip.get_info(technology=technology, version=version)
        if local_ip.version == version:
            console.print(
                f"[white]The IP [magenta]{ip}"
                f"[white] is up to date; version {local_ip.version}"
            )
        else:
            if update:
                console.print(f"Updating {ip}[white]...")
                uninstall_ip(console, ipm_iproot, ip, local_ip.ip_root, deps_file=local_ip.ip_root)
                install_ip(
                    console=console,
                    ipm_iproot=ipm_iproot,
                    ip=ip,
                    overwrite=True,
                    technology=technology,
                    version=version,
                    ip_root=local_ip.ip_root,
                    deps_file=local_ip.ip_root
                )
            else:
                console.print(
                    f"[yellow]The IP [magenta]{ip}"
                    f"[yellow] has a newer version {remote_ip.version} to update the IP run [white]'ipm update --ip {ip}'"
                )


def check_hierarchy(console, ip_path, ip, json_path):
    common_dirs = ["verify/beh_model", "fw", "hdl/rtl/bus_wrapper"]
    with open(json_path) as json_file:
        data = json.load(json_file)
    # check the folder hierarchy
    if data["type"] == "hard":
        ipm_dirs = ["hdl/gl", "timing/lib", "timing/sdf", "timing/spef", "layout/gds", "layout/lef"]
    elif data["type"] == "soft" and data["category"] == "digital":
        ipm_dirs = ["hdl/rtl/design", "verify/utb", "pnr"]
    if data["category"] == "analog":
        ipm_dirs = ["spice"]
    ipm_dirs = ipm_dirs + common_dirs
    ipm_files = [f"{ip}.json", "readme.md", "doc/datasheet.pdf"]
    flag = True
    for dirs in ipm_dirs:
        if not checkdir(os.path.join(ip_path, dirs)):
            console.print(
                f"[red]The directory {dirs} cannot be found under {ip_path} please refer to the ipm directory structure"
            )
            flag = False

    for files in ipm_files:
        if not os.path.exists(os.path.join(ip_path, files)):
            console.print(
                f"[red]The file {files} cannot be found under {ip_path} please refer to the ipm directory structure"
            )
            flag = False
    return flag


def check_JSON(console, JSON_path, ip):
    if not os.path.exists(JSON_path):
        console.print(
            f"[red]Can't find {JSON_path} please refer to the ipm directory structure (IP name {ip} might be wrong)"
        )
        return False
    json_fields = [
        "name",
        "repo",
        "version",
        "author",
        "email",
        "date",
        "type",
        "category",
        "status",
        "width",
        "height",
        "technology",
        "tag",
        "cell_count",
        "clk_freq",
        "license"
    ]
    flag = True
    with open(JSON_path) as json_file:
        json_decoded = json.load(json_file)

    if ip is not json_decoded["name"]:
        console.print(f"[red]The given IP name {ip} is not the same as the one in json file")
        flag = False

    for field in json_fields:
        if field not in json_decoded.keys():
            console.print(
                f"[red]The field '{field}' was not included in the {ip}.json file"
            )
            flag = False

    return flag


def package_check(console, ipm_iproot, ip, version, gh_repo):
    if gh_repo.startswith("https"):
        gh_repo_url = gh_repo
    else:
        gh_repo_url = f"https://{gh_repo}"
    
    release_tag_url = f"{gh_repo_url}/releases/tag/{version}"
    
    # Generate only the specific URL format
    tarball_url = None
    
    # If GitHub repo, use the specific format
    if "github.com" in gh_repo_url:
        repo_parts = gh_repo.split('/')
        if len(repo_parts) >= 3:  # domain/owner/repo format
            repo_name = repo_parts[-1]  # Extract repo name
            # Use only this specific URL format: https://github.com/chipfoundry/EF_AES/archive/refs/tags/EF_AES-v1.1.0.tar.gz
            tarball_url = f"{gh_repo_url}/archive/refs/tags/{repo_name}-{version}.tar.gz"
    else:
        # Default URL format for non-GitHub repos
        tarball_url = f"{gh_repo_url}/releases/download/{version}/{version}.tar.gz"
            
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    package_check_path = os.path.join(IPM_DIR_PATH, f"{ip}_pre-check")
    ip_path = os.path.join(package_check_path, ip)
    if checkdir(package_check_path):
        shutil.rmtree(package_check_path)

    # Set up headers with authentication if GitHub token is available
    headers = {}
    if GITHUB_TOKEN and "github.com" in gh_repo_url:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        console.print(f"[green] Using GitHub authentication for repository checks")

    console.print("[magenta][STEP 1]:", "Checking the GitHub repo")
    repo_response = requests.get(gh_repo_url, stream=True, headers=headers)
    if repo_response.status_code == 404:
        console.print(f"[red]The GitHub repo {gh_repo} does not exist")
    elif repo_response.status_code in [401, 403]:
        console.print(f"[red]Authentication issue accessing GitHub repo {gh_repo}. Check your GITHUB_TOKEN.")
    elif repo_response.status_code == 200:  # The repo exists, check for the release
        console.print(
            "[magenta][STEP 2]:",
            f"Checking for the release with the tag {version}",
        )
        release_tag_response = requests.get(release_tag_url, stream=True, headers=headers)
        if release_tag_response.status_code == 404:
            console.print(
                f"[red]There is no release tagged {version} in the GitHub repo {gh_repo}"
            )
        elif release_tag_response.status_code in [401, 403]:
            console.print(f"[red]Authentication issue accessing GitHub release. Check your GITHUB_TOKEN.")
        elif release_tag_response.status_code == 200:  # Release exists, check for tarball
            console.print(
                "[magenta][STEP 3]:", f'Checking for the tarball at: {tarball_url}'
            )
            
            # Try the specific URL format
            console.print(f"[yellow]Trying URL: {tarball_url}")
            release_tarball_response = requests.get(tarball_url, stream=True, headers=headers, allow_redirects=True)
            
            if release_tarball_response.status_code != 200:
                console.print(
                    f"[red]No tarball found at {tarball_url}: HTTP {release_tarball_response.status_code}"
                )
            elif release_tarball_response.status_code in [401, 403]:
                console.print(f"[red]Authentication issue accessing GitHub tarball. Check your GITHUB_TOKEN.")
            else:  # Tarball exists under the correct tag name, download it
                console.print(f"[green]Found tarball at: {tarball_url}")
                os.makedirs(package_check_path, exist_ok=True)
                tarball_path = os.path.join(package_check_path, f"{version}.tar.gz")
                with open(tarball_path, "wb") as f:
                    f.write(release_tarball_response.content)
                file = tarfile.open(tarball_path)
                file.extractall(package_check_path)
                file.close()
                os.remove(tarball_path)
                console.print(
                    "[magenta][STEP 4]:", "Checking the JSON file content"
                )
                
                # Handle GitHub archive format
                extracted_contents = os.listdir(package_check_path)
                if len(extracted_contents) == 1 and os.path.isdir(os.path.join(package_check_path, extracted_contents[0])):
                    # Move files from nested directory to ip_path
                    console.print(f"[green]Found GitHub-style archive with root directory: {extracted_contents[0]}")
                    nested_dir = os.path.join(package_check_path, extracted_contents[0])
                    os.makedirs(ip_path, exist_ok=True)
                    
                    for item in os.listdir(nested_dir):
                        s = os.path.join(nested_dir, item)
                        d = os.path.join(ip_path, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                else:
                    # If the extracted files are already at the correct level
                    # Just rename the directory if needed
                    if not os.path.exists(ip_path):
                        os.makedirs(ip_path, exist_ok=True)
                        for item in extracted_contents:
                            src = os.path.join(package_check_path, item)
                            dst = os.path.join(ip_path, item)
                            if os.path.isdir(src):
                                shutil.copytree(src, dst)
                            else:
                                shutil.copy2(src, dst)
                
                json_path = os.path.join(ip_path, f"{ip}.json")
                valid_JSON = check_JSON(console, json_path, ip)
                if valid_JSON:
                    console.print(
                        "[magenta][STEP 5]:", "Checking the hierarchy of the directory"
                    )
                    valid_hierarchy = check_hierarchy(
                        console, ip_path, ip, json_path
                    )  # Checks if folder's hierarchy is valid
                    if valid_hierarchy:
                        console.print(
                            "[green]IP pre-check was successful you can now submit your IP"
                        )
                shutil.rmtree(package_check_path)
