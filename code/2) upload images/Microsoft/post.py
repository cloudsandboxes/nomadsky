"""
Before running, install dependencies:

pip install azure-identity azure-storage-blob requests
"""

import os
import requests
import json
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, ContentSettings

# -------------------------------
# VARIABLES
# -------------------------------
subscription_id = "<SUBSCRIPTION_ID>"
resource_group  = "<RESOURCE_GROUP>"
location        = "westeurope"
storage_account = "mystorage" + os.urandom(4).hex()
container_name  = "vhds"
vhd_local_path  = r"C:\Temp\osdisk.vhd"
vhd_name        = "osdisk.vhd"
vm_name         = "<NEW_VM_NAME>"
vm_size         = "Standard_DS1_v2"
admin_username  = "<USERNAME>"
admin_password  = "<PASSWORD>"
vnet_name       = "<VNET_NAME>"
subnet_name     = "<SUBNET_NAME>"

# -------------------------------
# 0) GET ACCESS TOKEN
# -------------------------------
credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# -------------------------------
# 1) CREATE STORAGE ACCOUNT
# -------------------------------
storage_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}?api-version=2023-01-01"
storage_payload = {
    "sku": {"name": "Standard_LRS"},
    "kind": "StorageV2",
    "location": location,
    "properties": {}
}

resp = requests.put(storage_url, headers=headers, data=json.dumps(storage_payload))
resp.raise_for_status()
print(f"Storage account {storage_account} created.")

# -------------------------------
# 2) CREATE BLOB CONTAINER
# -------------------------------
container_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}/blobServices/default/containers/{container_name}?api-version=2022-11-02"
container_payload = {"properties": {}}

resp = requests.put(container_url, headers=headers, data=json.dumps(container_payload))
resp.raise_for_status()
print(f"Container {container_name} created.")

# -------------------------------
# 3) GET STORAGE ACCOUNT KEY
# -------------------------------
keys_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}/listKeys?api-version=2023-01-01"
keys_resp = requests.post(keys_url, headers=headers)
keys_resp.raise_for_status()
storage_key = keys_resp.json()["keys"][0]["value"]

# -------------------------------
# 4) UPLOAD VHD TO STORAGE ACCOUNT (chunked)
# -------------------------------
vhd_uri = f"https://{storage_account}.blob.core.windows.net/{container_name}/{vhd_name}"
blob = BlobClient(account_url=f"https://{storage_account}.blob.core.windows.net/",
                  container_name=container_name,
                  blob_name=vhd_name,
                  credential=storage_key)

print(f"Uploading {vhd_local_path} to {vhd_uri} in chunks ...")
chunk_size = 8 * 1024 * 1024  # 8 MB

with open(vhd_local_path, "rb") as f:
    blob.upload_blob(f, overwrite=True, blob_type="BlockBlob", length=os.path.getsize(vhd_local_path),
                     content_settings=ContentSettings(content_type='application/octet-stream'))
print("Upload complete.")

# -------------------------------
# 5) CREATE NIC
# -------------------------------
nic_name = f"{vm_name}-nic"
nic_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkInterfaces/{nic_name}?api-version=2023-05-01"

nic_payload = {
    "location": location,
    "properties": {
        "ipConfigurations": [
            {
                "name": f"{nic_name}-ipconfig",
                "properties": {
                    "subnet": {"id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}"},
                    "privateIPAllocationMethod": "Dynamic"
                }
            }
        ]
    }
}

resp = requests.put(nic_url, headers=headers, data=json.dumps(nic_payload))
resp.raise_for_status()
print(f"NIC {nic_name} created.")

# -------------------------------
# 6) CREATE VM FROM VHD
# -------------------------------
vm_payload = {
    "location": location,
    "properties": {
        "hardwareProfile": {"vmSize": vm_size},
        "storageProfile": {
            "osDisk": {
                "osType": "Windows",  # or Linux
                "name": f"{vm_name}_osdisk",
                "createOption": "Attach",
                "vhd": {"uri": vhd_uri}
            },
            "dataDisks": []
        },
        "osProfile": {
            "computerName": vm_name,
            "adminUsername": admin_username,
            "adminPassword": admin_password
        },
        "networkProfile": {
            "networkInterfaces": [{"id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkInterfaces/{nic_name}", "properties": {"primary": True}}]
        }
    }
}

vm_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}?api-version=2023-03-01"
resp = requests.put(vm_url, headers=headers, data=json.dumps(vm_payload))
resp.raise_for_status()
print(f"VM {vm_name} creation request submitted successfully.")

