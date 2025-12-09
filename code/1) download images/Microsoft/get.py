import requests
import time
import json
import os
from azure.identity import DefaultAzureCredential
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient


# -------------------------------
# VARIABLES
# -------------------------------
subscription_id = "<SUBSCRIPTION_ID>"
resource_group  = "<RESOURCE_GROUP>"
TARGET_VM_NAME  = "<VM_NAME>"
output_vhd_path = r"C:\Temp\osdisk.vhd"

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_headers(credential):
    """Get fresh authorization headers"""
    token = credential.get_token("https://management.azure.com/.default").token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def poll_async_operation(operation_url, credential, timeout=600, poll_interval=5):
    """Poll an Azure async operation until complete"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        headers = get_headers(credential)
        resp = requests.get(operation_url, headers=headers)
        resp.raise_for_status()
        
        status = resp.json().get("status", "Unknown")
        print(f"Operation status: {status}")
        
        if status == "Succeeded":
            return resp.json()
        elif status == "Failed":
            raise Exception(f"Operation failed: {resp.json()}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Operation timed out after {timeout} seconds")

# -------------------------------
# MAIN SCRIPT
# -------------------------------

# -------------------------------
# MAIN SCRIPT
# -------------------------------

Login step 
# Login 

# Authenticate using DefaultAzureCredential (supports environment, VS Code, CLI login, etc.)
credential = DefaultAzureCredential()

subscription_client = SubscriptionClient(credential)

vm_found = False

for sub in subscription_client.subscriptions.list():
    subscription_id = sub.subscription_id
    compute_client = ComputeManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    for rg in resource_client.resource_groups.list():
        resource_group_name = rg.name
        try:
            vm = compute_client.virtual_machines.get(resource_group_name, TARGET_VM_NAME)
        except Exception:
            continue  # VM not found in this resource group

        # VM found
        vm_found = True

        # VM basic info
        vm_name = vm.name
        vm_size = vm.hardware_profile.vm_size
        os_type = vm.storage_profile.os_disk.os_type.value
        resource_id = vm.id

        # Get network interface
        nic_id = vm.network_profile.network_interfaces[0].id
        nic_name = nic_id.split('/')[-1]
        nic_rg = nic_id.split('/')[4]
        nic = network_client.network_interfaces.get(nic_rg, nic_name)

        # Subnet info
        subnet = nic.ip_configurations[0].subnet
        subnet_range = subnet.address_prefix if subnet else "N/A"

        # Public IP if exists
        public_ip_address = "None"
        if nic.ip_configurations[0].public_ip_address:
            public_ip_id = nic.ip_configurations[0].public_ip_address.id
            public_ip_name = public_ip_id.split('/')[-1]
            public_ip_rg = public_ip_id.split('/')[4]
            public_ip = network_client.public_ip_addresses.get(public_ip_rg, public_ip_name)
            public_ip_address = public_ip.ip_address or "None"

        # Print info
        print(f"VM Name: {vm_name}")
        print(f"OS: {os_type}")
        print(f"Size: {vm_size}")
        print(f"Resource ID: {resource_id}")
        print(f"Subnet Range: {subnet_range}")
        print(f"Public IP: {public_ip_address}")
        break

    if vm_found:
        break

if not vm_found:
    print("Specific VM not found, check credentials or VM name.")




try:
    credential = DefaultAzureCredential()
    
    # -------------------------------
    # 1) DEALLOCATE THE VM (not just power off)
    # -------------------------------
    print("Deallocating VM (this stops billing)...")
    deallocate_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
        f"/virtualMachines/{vm_name}/deallocate?api-version=2023-03-01"
    )
    
    headers = get_headers(credential)
    resp = requests.post(deallocate_uri, headers=headers)
    resp.raise_for_status()
    
    # Check if there's an async operation location
    if "Azure-AsyncOperation" in resp.headers:
        print("Waiting for VM to deallocate...")
        poll_async_operation(resp.headers["Azure-AsyncOperation"], credential)
        print("VM deallocated successfully.")
    else:
        print("VM deallocate request submitted.")
        time.sleep(30)  # fallback wait
    
    # -------------------------------
    # 2) GET OS DISK INFO
    # -------------------------------
    print("\nGetting OS disk information...")
    get_vm_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
        f"/virtualMachines/{vm_name}?api-version=2023-03-01"
    )
    
    headers = get_headers(credential)
    vm_resp = requests.get(get_vm_uri, headers=headers)
    vm_resp.raise_for_status()
    vm = vm_resp.json()
    
    os_disk_id = vm["properties"]["storageProfile"]["osDisk"]["managedDisk"]["id"]
    disk_name = os_disk_id.split("/")[-1]
    print(f"OS Disk: {disk_name}")
    print(f"OS Disk ID: {os_disk_id}")
    
    # -------------------------------
    # 3) REQUEST DISK EXPORT (ASYNC)
    # -------------------------------
    print("\nRequesting disk export access...")
    export_uri = f"https://management.azure.com{os_disk_id}/beginGetAccess?api-version=2023-04-02"
    export_body = {
        "access": "Read",
        "durationInSeconds": 3600
    }
    
    headers = get_headers(credential)
    export_resp = requests.post(export_uri, headers=headers, json=export_body)
    export_resp.raise_for_status()
    
    # Get the async operation URL from Location or Azure-AsyncOperation header
    if "Location" in export_resp.headers:
        operation_url = export_resp.headers["Location"]
    elif "Azure-AsyncOperation" in export_resp.headers:
        operation_url = export_resp.headers["Azure-AsyncOperation"]
    else:
        raise Exception("No async operation URL found in response headers")
    
    print(f"Polling for SAS URL generation...")
    result = poll_async_operation(operation_url, credential, timeout=300)
    
    # The SAS URL should be in the result
    sas_url = result.get("properties", {}).get("output", {}).get("accessSAS")
    if not sas_url:
        # Try alternative location
        sas_url = result.get("accessSAS")
    
    if not sas_url:
        raise Exception(f"Could not find SAS URL in response: {result}")
    
    print("SAS URL obtained successfully.")
    
    # -------------------------------
    # 4) DOWNLOAD THE VHD
    # -------------------------------
    print(f"\nDownloading OS disk to {output_vhd_path}...")
    print("This may take a while depending on disk size...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_vhd_path), exist_ok=True)
    
    vhd_resp = requests.get(sas_url, stream=True)
    vhd_resp.raise_for_status()
    
    # Get file size if available
    total_size = int(vhd_resp.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_vhd_path, "wb") as f:
        for chunk in vhd_resp.iter_content(chunk_size=1024*1024):  # 1MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}% ({downloaded / (1024**3):.2f} GB)", end="")
    
    print(f"\n\n✓ Download complete: {output_vhd_path}")
    
    # Get file size
    file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)
    print(f"File size: {file_size_gb:.2f} GB")
    
    # -------------------------------
    # 5) REVOKE ACCESS (OPTIONAL)
    # -------------------------------
    print("\nRevoking disk access...")
    revoke_uri = f"https://management.azure.com{os_disk_id}/endGetAccess?api-version=2023-04-02"
    headers = get_headers(credential)
    revoke_resp = requests.post(revoke_uri, headers=headers)
    if revoke_resp.status_code in [200, 202]:
        print("Disk access revoked.")
    
    print("\n✓ All operations completed successfully!")
    print(f"\nNote: VM '{vm_name}' is deallocated. Start it again when needed.")

except requests.exceptions.RequestException as e:
    print(f"\n✗ HTTP Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
