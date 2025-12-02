# AWS variables
# for downloading AWS images
region_name = "eu-west-1"
instance_id = "<INSTANCE_ID>"
output_file = r"C:\Temp\ec2_disk.vmdk"  # or .vhdx
s3_bucket = "<YOUR_S3_BUCKET>"
s3_prefix = "ec2-exports/"

#for uploading AWS images
region_name = "eu-west-1"
bucket_name = "<YOUR_S3_BUCKET>"
vmdk_local_path = r"C:\Temp\osdisk.vmdk"
vmdk_s3_key = "ec2-uploads/osdisk.vmdk"
role_name = "vmimport"  # Pre-created IAM role
ami_name = "Imported-AMI"
instance_type = "t2.micro"
key_name = "<YOUR_KEY_PAIR>"  # SSH key for Linux or leave for Windows

# Google variables
# for downloading Google images

project_id = "<PROJECT_ID>"
zone = "<ZONE>"  # e.g., "europe-west1-b"
instance_name = "<INSTANCE_NAME>"
output_file = r"C:\Temp\gcp_disk.vmdk"  # or .vhd
bucket_name = "<GCS_BUCKET>"

#for uploading Google images

project_id = "<PROJECT_ID>"
zone = "europe-west1-b"
instance_name = "<NEW_VM_NAME>"
disk_local_path = r"C:\Temp\osdisk.vmdk"  # VMDK or VHD
bucket_name = "<GCS_BUCKET>"
gcs_object_name = f"osdisk/{os.path.basename(disk_local_path)}"
machine_type = "e2-medium"

# Azure variables
# for downloading Azure images

subscription_id = "<SUBSCRIPTION_ID>"
resource_group  = "<RESOURCE_GROUP>"
vm_name         = "<VM_NAME>"
location        = "westeurope"
storage_name    = f"mystorage{os.urandom(4).hex()}"  # equivalent to Get-Random
container_name  = "vhds"
output_vhd_path = r"C:\Temp\osdisk.vhd"

#for uploading Azure images
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

