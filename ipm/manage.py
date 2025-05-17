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
import click
import json
from rich.console import Console

from .common import (
    check_ip_root_dir,
    get_IP_info,
    install_deps_ip,
    list_IPs_local,
    opt_ipm_iproot,
    list_IPs,
    install_ip,
    package_check,
    uninstall_ip,
    get_IP_list,
    check_IP,
    check_ipm_directory,
    IP_DEFAULT_ROOT,
    LOCAL_JSON_FILE_NAME,
)

# Default installation path with environment variable override
DEFAULT_IP_ROOT = os.getenv("IP_ROOT") or os.path.join(os.path.expanduser("~"), ".ipm")


@click.command("ls-remote")
@opt_ipm_iproot
@click.option(
    "--category",
    required=False,
    help="Optionally provide the category (digital, comm, analog, dataconv)",
)
@click.option(
    "--technology",
    required=False,
    help="Optionally provide the technology (sky130, gf180mcu)",
)
def ls_remote_cmd(category, ipm_iproot, technology):
    """Lists all verified IPs in ipm's database"""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        if category is not None:
            if category in ["digital", "comm", "analog", "dataconv"]:
                console.print(f"[green]Verified IPs for the {category} category:")
                list_IPs(console, ipm_iproot, remote=True, category=category)
            else:
                console.print(
                    "You entered a wrong category, invoke ipm ls --help for assistance"
                )
        elif technology is not None:
            if technology in ["sky130", "gf180mcu"]:
                console.print(f"[green]Verified IPs for the {technology} technology:")
                list_IPs(console, ipm_iproot, remote=True)
            else:
                console.print(
                    "You entered a wrong technology, invoke ipm ls --help for assistance"
                )
        else:
            console.print("[green]Verified IPs:")
            list_IPs(console, ipm_iproot, remote=True)


def ls_remote(category, ipm_iproot, technology):
    """Lists all verified IPs in ipm's database"""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        if category is not None:
            if category in ["digital", "comm", "analog", "dataconv"]:
                console.print(f"[green]Verified IPs for the {category} category:")
                list_IPs(console, ipm_iproot, remote=True, category=category)
            else:
                console.print(
                    "You entered a wrong category, invoke ipm ls --help for assistance"
                )
        elif technology is not None:
            if technology in ["sky130", "gf180mcu"]:
                console.print(f"[green]Verified IPs for the {technology} technology:")
                list_IPs(console, ipm_iproot, remote=True)
            else:
                console.print(
                    "You entered a wrong technology, invoke ipm ls --help for assistance"
                )
        else:
            console.print("[green]Verified IPs:")
            list_IPs(console, ipm_iproot, remote=True)


@click.command("ls")
@opt_ipm_iproot
@click.option(
    "--category",
    required=False,
    help="Optionally provide the category (digital, comm, analog, dataconv)",
)
@click.option(
    "--technology",
    required=False,
    help="Optionally provide the technology (sky130, gf180mcu)",
)
@click.option("--ip-root", required=False, default=DEFAULT_IP_ROOT, help="IP installation path (default: $IP_ROOT if set, otherwise ~/.ipm)")
def ls_cmd(category, ipm_iproot, technology, ip_root):
    """Lists all locally installed IPs"""
    console = Console()
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        if category is not None:
            if category in ["digital", "comm", "analog", "dataconv"]:
                console.print(
                    f"[green]Installed IPs at {ip_root} for the {category} category:"
                )
                list_IPs_local(console, ipm_iproot, remote=False, category=category, ip_root=ip_root)
            else:
                console.print(
                    "You entered a wrong category, invoke ipm ls --help for assistance"
                )
        elif technology is not None:
            if technology in ["sky130", "gf180mcu"]:
                console.print(
                    f"[green]Installed IPs at {ip_root} for the {technology} technology:"
                )
                list_IPs_local(console, ipm_iproot, remote=False, ip_root=ip_root)
            else:
                console.print(
                    "You entered a wrong technology, invoke ipm ls --help for assistance"
                )
        else:
            console.print(f"[green]Installed IPs at {ip_root}:")
            list_IPs_local(console, ipm_iproot, remote=False, ip_root=ip_root)


def ls(category, ipm_iproot, technology, ip_root=None):
    """Lists all locally installed IPs"""
    if ip_root is None:
        ip_root = DEFAULT_IP_ROOT
        
    console = Console()
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        if category is not None:
            if category in ["digital", "comm", "analog", "dataconv"]:
                console.print(
                    f"[green]Installed IPs at {ip_root} for the {category} category:"
                )
                list_IPs_local(console, ipm_iproot, remote=False, category=category, ip_root=ip_root)
            else:
                console.print(
                    "You entered a wrong category, invoke ipm ls --help for assistance"
                )
        elif technology is not None:
            if technology in ["sky130", "gf180mcu"]:
                console.print(
                    f"[green]Installed IPs at {ip_root} for the {technology} technology:"
                )
                list_IPs_local(console, ipm_iproot, remote=False, ip_root=ip_root)
            else:
                console.print(
                    "You entered a wrong technology, invoke ipm ls --help for assistance"
                )
        else:
            console.print(f"[green]Installed IPs at {ip_root}:")
            list_IPs_local(console, ipm_iproot, remote=False, ip_root=ip_root)


@click.command("output")
@opt_ipm_iproot
def output_cmd(ipm_iproot):
    """(Default) Outputs the current IP installation path"""
    console = Console()
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        print(f"Your IPs will be installed at {IPM_DIR_PATH}")


def output(ipm_iproot):
    """(Default) Outputs the current IP installation path"""
    console = Console()
    IPM_DIR_PATH = os.path.join(ipm_iproot)
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        return IPM_DIR_PATH


@click.command("install")
@click.argument("ip")
@click.option(
    "--overwrite",
    required=False,
    is_flag=True,
    default=False,
    help="Overwrite IP",
)
@click.option("--technology", required=False, default="sky130", help="Install IP based on technology")
@click.option("--version", required=False, help="Install IP with a specific version")
@click.option("--ip-root", required=False, default=DEFAULT_IP_ROOT, help="IP installation path (default: $IP_ROOT if set, otherwise ~/.ipm)")
@click.option("--deps-file", required=False, help="dependencies file path")
@opt_ipm_iproot
def install_cmd(ip, ip_root, ipm_iproot, overwrite, technology="sky130", version=None, deps_file=None):
    """Install one of the verified IPs locally"""
    console = Console()
    
    valid_ipm_dir = check_ipm_directory(console, ipm_iproot)
    valid_ip_dir = check_ip_root_dir(console, ip_root)
    
    if valid_ipm_dir and valid_ip_dir:
        install(
            console, ip, ipm_iproot, overwrite, technology=technology, version=version, ip_root=ip_root, deps_file=deps_file
        )


def install(
    console,
    ip,
    ipm_iproot,
    overwrite,
    technology="sky130",
    version=None,
    ip_root=None,
    deps_file=None,
):
    """Install one of the verified IPs locally"""
    # Use the environment-aware default if ip_root is None
    if ip_root is None:
        ip_root = IP_DEFAULT_ROOT
        
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=True)
        if ip not in IP_list:
            print(
                "Please provide a valid IP name, to check all the available IPs invoke 'ipm ls'"
            )
        else:
            install_ip(
                console=console,
                ipm_iproot=ipm_iproot,
                ip=ip,
                overwrite=overwrite,
                technology=technology,
                version=version,
                ip_root=ip_root,
                deps_file=deps_file
            )


@click.command("install-dep")
@click.option(
    "--overwrite",
    required=False,
    is_flag=True,
    default=False,
    help="Overwrite IP",
)
@click.option("--ip-root", required=False, default=DEFAULT_IP_ROOT, help="IP installation path (default: $IP_ROOT if set, otherwise ~/.ipm)")
@click.option("--dep-file", required=False, help="dependencies file path")
@opt_ipm_iproot
def install_deps_cmd(ip_root, ipm_iproot, overwrite, dep_file=None):
    """Install verified IPs from dependencies json file"""
    console = Console()
    valid_ipm_dir = check_ipm_directory(console, ipm_iproot)
    valid_ip_dir = check_ip_root_dir(console, ip_root)
    if valid_ipm_dir and valid_ip_dir:
        install_deps(
            console, ipm_iproot, overwrite, ip_root=ip_root, deps_file=dep_file
        )


def install_deps(
    console,
    ipm_iproot,
    overwrite,
    ip_root=None,
    deps_file=None,
):
    """Install verified IPs from dependencies json file"""
    # Use the environment-aware default if ip_root is None
    if ip_root is None:
        ip_root = IP_DEFAULT_ROOT
        
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=True)
        install_deps_ip(
            console=console,
            ipm_iproot=ipm_iproot,
            overwrite=overwrite,
            ip_root=ip_root,
            deps_file=deps_file,
            IP_list=IP_list
        )


@click.command("uninstall")
@click.argument("ip")
@click.option("--ip-root", required=False, default=DEFAULT_IP_ROOT, help="IP installation path (default: $IP_ROOT if set, otherwise ~/.ipm)")
@click.option("--dep-file", required=False, help="dependencies file path")
@opt_ipm_iproot
def uninstall_cmd(ip, ipm_iproot, ip_root, dep_file):
    """Uninstall one of the IPs installed locally"""
    console = Console()
    valid_ipm_dir = check_ipm_directory(console, ipm_iproot)
    valid_ip_dir = check_ip_root_dir(console, ip_root)
    if valid_ipm_dir and valid_ip_dir:
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if ip not in IP_list:
            print(
                "Please provide a valid IP name, to check all installed IPs invoke 'ipm ls'"
            )
        else:
            uninstall_ip(console, ipm_iproot, ip, ip_root, dep_file)


@click.command("check")
@click.option(
    "--ip",
    required=False,
    help="Optionally provide an IP to check for its newer version",
)
@opt_ipm_iproot
def check_cmd(ip, ipm_iproot):
    """Check for new versions of all installed IPs or a specific IP."""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if ip is not None:
            if ip not in IP_list:
                print(
                    "Please provide a valid IP name, to check all installed IPs invoke 'ipm ls'"
                )
            else:
                check_IP(console, ipm_iproot, ip, update=False)
        else:
            check_IP(console, ipm_iproot, "all", update=False)


def check(console, ip, ipm_iproot, version):
    """Check for new versions of all installed IPs or a specific IP."""
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if ip is not None:
            if ip not in IP_list:
                print(
                    "Please provide a valid IP name, to check all installed IPs invoke 'ipm ls'"
                )
            else:
                check_IP(console, ipm_iproot, ip, update=True, version=version)
        else:
            check_IP(console, ipm_iproot, "all", update=True, version=version)


@click.command("update")
@click.option("--ip", required=False, help="Provide an IP to update")
@click.option("--all", required=False, is_flag=True, help="Updates all installed IPs")
@opt_ipm_iproot
def update_cmd(ip, all, ipm_iproot):
    """Update all installed IPs to their latest versions or a specific IP."""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if ip is not None:
            if ip not in IP_list:
                print(
                    "Please provide a valid IP name, to check all installed IPs invoke 'ipm ls'"
                )
            else:
                check_IP(console, ipm_iproot, ip, update=True)
        else:
            if all:
                check_IP(console, ipm_iproot, "all", update=True)
            else:
                console.print(
                    "Either provide an ip name or to update all installed IPs run 'ipm update --all'"
                )


def update(ip, all, ipm_iproot):
    """Update all installed IPs to their latest versions or a specific IP."""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        IP_list = get_IP_list(ipm_iproot, remote=False)
        if ip is not None:
            if ip not in IP_list:
                print(
                    "Please provide a valid IP name, to check all installed IPs invoke 'ipm ls'"
                )
            else:
                check_IP(console, ipm_iproot, ip, update=True)
        else:
            if all:
                check_IP(console, ipm_iproot, "all", update=True)
            else:
                console.print(
                    "Either provide an ip name or to update all installed IPs run 'ipm update --all'"
                )


@click.command("package-check")
@click.option("--name", required=True, help="Provide IP name")
@click.option("--version", required=True, help="Provide IP version")
@click.option("--url", required=True, help="Provide IP url")
@opt_ipm_iproot
def package_check_cmd(ipm_iproot, name, version, url):
    """Check packaged IP."""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        package_check(console, ipm_iproot, name, version, url)


@click.command("info")
@click.argument("ip")
@opt_ipm_iproot
def info_cmd(ipm_iproot, ip):
    """list all versions and info of the IP"""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        get_IP_info(console, ipm_iproot, ip, remote=True)


def info(ipm_iproot, ip):
    """list all versions and info of the IP"""
    console = Console()
    valid = check_ipm_directory(console, ipm_iproot)
    if valid:
        get_IP_info(console, ipm_iproot, ip, remote=True)


@click.command("cleanup")
@opt_ipm_iproot
@click.option("--ip-root", required=False, default=DEFAULT_IP_ROOT, help="IP installation path (default: $IP_ROOT if set, otherwise ~/.ipm)")
@click.option("--force", is_flag=True, default=False, help="Remove entries without confirmation")
def cleanup_cmd(ipm_iproot, ip_root, force):
    """Clean up IP entries that are not in the specified IP root directory"""
    console = Console()
    valid_ipm_dir = check_ipm_directory(console, ipm_iproot)
    valid_ip_dir = check_ip_root_dir(console, ip_root)
    
    if not valid_ipm_dir or not valid_ip_dir:
        return
    
    json_file_path = os.path.join(ipm_iproot, LOCAL_JSON_FILE_NAME)
    with open(json_file_path) as json_file:
        data = json.load(json_file)
    
    # Keep track of changes
    removed_entries = []
    entries_to_remove = []
    
    # Check whether we have the old format or new format JSON
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data.get(first_key, {}):
        # New format - IPs are indexed by name directly
        for ip_name, ip_data in list(data.items()):
            stored_ip_root = ip_data.get("ip_root", "")
            if stored_ip_root and stored_ip_root != ip_root:
                # IP installed in different location
                entries_to_remove.append((ip_name, stored_ip_root))
    else:
        # Original format - IPs are in categories
        for category, values in data.items():
            for value in list(values):
                stored_ip_root = value.get("ip_root", "")
                ip_name = value.get("name", "")
                if stored_ip_root and stored_ip_root != ip_root:
                    # IP installed in different location
                    entries_to_remove.append((ip_name, stored_ip_root))
    
    if not entries_to_remove:
        console.print("[green]No entries found that need cleanup.")
        return
    
    # Show entries to be removed
    console.print(f"[yellow]Found {len(entries_to_remove)} entries that point to a different IP root:")
    for ip_name, stored_ip_root in entries_to_remove:
        console.print(f"  - {ip_name} (installed at {stored_ip_root})")
    
    if not force:
        confirm = input("\nDo you want to remove these entries? (y/n): ")
        if confirm.lower() != 'y':
            console.print("[yellow]Cleanup canceled.")
            return
    
    # Remove entries
    if first_key and first_key in data and "description" in data.get(first_key, {}):
        # New format
        for ip_name, stored_ip_root in entries_to_remove:
            if ip_name in data:
                del data[ip_name]
                removed_entries.append(ip_name)
    else:
        # Original format
        for category, values in data.items():
            data[category] = [v for v in values if (v.get("name", ""), v.get("ip_root", "")) not in entries_to_remove]
            removed_entries.extend([e[0] for e in entries_to_remove if e[0] not in removed_entries])
    
    # Save updated data
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file)
    
    console.print(f"[green]Successfully removed {len(removed_entries)} entries from the registry.")
    console.print("[yellow]Note: The actual files were not deleted, only the registry entries.")


def cleanup(ipm_iproot, ip_root, force=False):
    """Clean up IP entries that are not in the specified IP root directory"""
    console = Console()
    valid_ipm_dir = check_ipm_directory(console, ipm_iproot)
    valid_ip_dir = check_ip_root_dir(console, ip_root)
    
    if not valid_ipm_dir or not valid_ip_dir:
        return
    
    json_file_path = os.path.join(ipm_iproot, LOCAL_JSON_FILE_NAME)
    with open(json_file_path) as json_file:
        data = json.load(json_file)
    
    # Keep track of changes
    removed_entries = []
    entries_to_remove = []
    
    # Check whether we have the old format or new format JSON
    first_key = next(iter(data)) if data else None
    if first_key and first_key in data and "description" in data.get(first_key, {}):
        # New format - IPs are indexed by name directly
        for ip_name, ip_data in list(data.items()):
            stored_ip_root = ip_data.get("ip_root", "")
            if stored_ip_root and stored_ip_root != ip_root:
                # IP installed in different location
                entries_to_remove.append((ip_name, stored_ip_root))
    else:
        # Original format - IPs are in categories
        for category, values in data.items():
            for value in list(values):
                stored_ip_root = value.get("ip_root", "")
                ip_name = value.get("name", "")
                if stored_ip_root and stored_ip_root != ip_root:
                    # IP installed in different location
                    entries_to_remove.append((ip_name, stored_ip_root))
    
    if not entries_to_remove:
        console.print("[green]No entries found that need cleanup.")
        return
    
    # Show entries to be removed
    console.print(f"[yellow]Found {len(entries_to_remove)} entries that point to a different IP root:")
    for ip_name, stored_ip_root in entries_to_remove:
        console.print(f"  - {ip_name} (installed at {stored_ip_root})")
    
    if not force:
        confirm = input("\nDo you want to remove these entries? (y/n): ")
        if confirm.lower() != 'y':
            console.print("[yellow]Cleanup canceled.")
            return
    
    # Remove entries
    if first_key and first_key in data and "description" in data.get(first_key, {}):
        # New format
        for ip_name, stored_ip_root in entries_to_remove:
            if ip_name in data:
                del data[ip_name]
                removed_entries.append(ip_name)
    else:
        # Original format
        for category, values in data.items():
            data[category] = [v for v in values if (v.get("name", ""), v.get("ip_root", "")) not in entries_to_remove]
            removed_entries.extend([e[0] for e in entries_to_remove if e[0] not in removed_entries])
    
    # Save updated data
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file)
    
    console.print(f"[green]Successfully removed {len(removed_entries)} entries from the registry.")
    console.print("[yellow]Note: The actual files were not deleted, only the registry entries.")
