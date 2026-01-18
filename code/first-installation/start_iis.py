#!/usr/bin/env python3
"""
Python script to start IIS (Internet Information Services) on Windows
This script must be run with Administrator privileges

prompt:now i need a python script that starts the IIS role.
python start_iis.py

second prompt: make def for making IIS path the git instead of enetpub 
"""

import subprocess
import sys
import ctypes
import time

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command, description):
    """Run a PowerShell command and return the result"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {description} completed successfully")
        if result.stdout.strip():
            print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        if e.stderr:
            print(f"  Error message: {e.stderr.strip()}")
        return False

def check_iis_installed():
    """Check if IIS is installed"""
    print("\nChecking if IIS is installed...")
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-WindowsFeature -Name Web-Server"],
            capture_output=True,
            text=True
        )
        
        if "Installed" in result.stdout:
            print("✓ IIS is installed")
            return True
        else:
            print("✗ IIS is not installed")
            return False
    except Exception as e:
        print(f"✗ Error checking IIS installation: {e}")
        return False

def install_iis():
    """Install IIS if not already installed"""
    print("\nAttempting to install IIS...")
    print("This may take several minutes...")
    
    command = "Install-WindowsFeature -Name Web-Server -IncludeManagementTools"
    return run_command(command, "IIS installation")

def start_iis_service():
    """Start the IIS service"""
    return run_command("Start-Service W3SVC", "Starting IIS service (W3SVC)")

def start_was_service():
    """Start the Windows Process Activation Service"""
    return run_command("Start-Service WAS", "Starting Windows Process Activation Service (WAS)")

def get_iis_status():
    """Get the current status of IIS services"""
    print("\n" + "="*50)
    print("IIS Service Status:")
    print("="*50)
    
    services = ["W3SVC", "WAS"]
    for service in services:
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Service {service} | Select-Object Name, Status, StartType"],
                capture_output=True,
                text=True
            )
            print(f"\n{result.stdout.strip()}")
        except Exception as e:
            print(f"Could not get status for {service}: {e}")

def test_iis():
    """Test if IIS is responding"""
    print("\n" + "="*50)
    print("Testing IIS...")
    print("="*50)
    
    try:
        import urllib.request
        print("\nAttempting to connect to http://localhost ...")
        response = urllib.request.urlopen("http://localhost", timeout=5)
        print(f"✓ IIS is responding! (Status code: {response.status})")
        print("  You can access IIS at: http://localhost")
        return True
    except Exception as e:
        print(f"✗ Could not connect to IIS: {e}")
        print("  IIS may need a moment to start, or Windows Firewall may be blocking it")
        return False

def main():
    print("="*50)
    print("IIS Starter Script")
    print("="*50)
    
    # Check if running as administrator
    if not is_admin():
        print("\n✗ ERROR: This script must be run as Administrator!")
        print("Please right-click Python and select 'Run as Administrator'")
        print("Or run from an elevated PowerShell/Command Prompt")
        sys.exit(1)
    
    print("✓ Running with Administrator privileges")
    
    # Check if IIS is installed
    if not check_iis_installed():
        print("\nIIS is not installed. Would you like to install it? (y/n): ", end="")
        choice = input().lower()
        
        if choice == 'y':
            if install_iis():
                print("✓ IIS has been installed successfully")
                time.sleep(2)  # Give the system a moment
            else:
                print("✗ Failed to install IIS")
                sys.exit(1)
        else:
            print("IIS installation cancelled")
            sys.exit(0)
    
    # Start IIS services
    print("\n" + "="*50)
    print("Starting IIS Services...")
    print("="*50)
    
    was_started = start_was_service()
    time.sleep(1)  # Brief pause between services
    
    w3svc_started = start_iis_service()
    
    if was_started and w3svc_started:
        print("\n✓ All IIS services started successfully!")
    else:
        print("\n⚠ Some services may have failed to start")
    
    # Get service status
    get_iis_status()
    
    # Test IIS
    time.sleep(2)  # Give IIS a moment to fully initialize
    test_iis()
    
    print("\n" + "="*50)
    print("Script completed!")
    print("="*50)

    setup_iis_site()

def setup_iis_site(site_name="testnomadsky",
                   physical_path=r"C:\Projects\nomadsky\code\nomadsky-engine\UI",
                   binding="*:80:"):
    """
    Create or update an IIS site pointing to a real folder.
    Requires IIS installed and admin privileges.
    
    :param site_name: Name of the IIS site
    :param physical_path: Folder to serve
    :param binding: IIS binding (default all IPs, port 80, no hostname)
    """
    
    # Check if site exists
    cmd_check = ["appcmd", "list", "site", site_name]
    result = subprocess.run(cmd_check, capture_output=True, text=True, shell=True)
    
    if "ERROR" in result.stdout or result.returncode != 0:
        # Site does not exist → create it
        cmd_create = [
            "appcmd", "add", "site",
            f"/name:{site_name}",
            f"/physicalPath:{physical_path}",
            f"/bindings:{binding}"
        ]
        subprocess.run(cmd_create, check=True, shell=True)
        print(f"IIS site '{site_name}' created, pointing to '{physical_path}'")
    else:
        # Site exists → update physical path
        cmd_update = [
            "appcmd", "set", "site",
            site_name,
            f"/[path='/'].physicalPath:{physical_path}"
        ]
        subprocess.run(cmd_update, check=True, shell=True)
        print(f"IIS site '{site_name}' updated to '{physical_path}'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
