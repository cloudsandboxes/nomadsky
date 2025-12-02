import requests
import time
import json
import os
from azure.identity import DefaultAzureCredential

# -------------------------------
# VARIABLES
# -------------------------------
subscription_id = "<SUBSCRIPTION_ID>"
resource_group  = "<RESOURCE_GROUP>"
vm_name         = "<VM_NAME>"
location        = "westeurope"
storage_name    = f"mystorage{os.urandom(4).hex()}"  # equivalent to Get-Random
container_name  = "vhds"
output_vhd_path = r"C:\Temp\osdisk.vhd"

# -------------------------------
# 0) GET ACCESS TOKEN
# -------------------------------
credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# -------------------------------
# 1) STOP THE VM
# -------------------------------
stop_vm_uri = (
    f"https://management.azure.com/subscriptions/{subscription_id}"
    f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
    f"/virtualMachines/{vm_name}/powerOff?api-version=2023-03-01"
)

print("Stopping VM...")
resp = requests.post(stop_vm_uri, headers=headers)
resp.raise_for_status()
print("VM stop request submitted.")

time.sleep(20)  # wait a bit for VM to stop

# -------------------------------
# 2) GET OS DISK + GENERATE SAS URL
# -------------------------------

# 2a) Get VM model to find OS disk ID
get_vm_uri = (
    f"https://management.azure.com/subscriptions/{subscription_id}"
    f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
    f"/virtualMachines/{vm_name}?api-version=2023-03-01"
)

vm = requests.get(get_vm_uri, headers=headers).json()
os_disk_id = vm["properties"]["storageProfile"]["osDisk"]["managedDisk"]["id"]
print(f"OS Disk ID: {os_disk_id}")

# 2b) Request SAS URL for exporting the disk
disk_name = os_disk_id.split("/")[-1]
export_uri = f"https://management.azure.com{os_disk_id}/beginGetAccess?api-version=2023-04-02"

export_body = {
    "access": "Read",
    "durationInSeconds": 3600
}

print("Requesting SAS URL...")
export_response = requests.post(export_uri, headers=headers, data=json.dumps(export_body)).json()
sas_url = export_response["accessSAS"]
print("SAS URL received.")

# -------------------------------
# 3) DOWNLOAD THE OS DISK VHD
# -------------------------------
print("Downloading OS Disk VHD... this may take a while.")
vhd_resp = requests.get(sas_url, stream=True)
vhd_resp.raise_for_status()

with open(output_vhd_path, "wb") as f:
    for chunk in vhd_resp.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Download complete: {output_vhd_path}")
