# -------------------------------
# VARIABLES
# -------------------------------
$subscriptionId = "<SUBSCRIPTION_ID>"
$resourceGroup  = "<RESOURCE_GROUP>"
$vmName         = "<VM_NAME>"
$location       = "westeurope"
$storageName    = "mystorage$(Get-Random)"
$containerName  = "vhds"
$outputVhdPath  = "C:\Temp\osdisk.vhd"

# Get access token for Azure REST
$token = (Get-AzAccessToken).Token
$headers = @{ Authorization = "Bearer $token" }

# -------------------------------
# 1) STOP THE VM
# -------------------------------
$stopVmUri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Compute/virtualMachines/$vmName/powerOff?api-version=2023-03-01"

Write-Host "Stopping VM..."
Invoke-RestMethod -Method Post -Uri $stopVmUri -Headers $headers

Start-Sleep -Seconds 20

# -------------------------------
# 2) GET OS DISK + GENERATE SAS URL
# -------------------------------
# 2a) Get VM model to find OS disk ID
$getVmUri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Compute/virtualMachines/$vmName?api-version=2023-03-01"

$vm = Invoke-RestMethod -Method Get -Uri $getVmUri -Headers $headers
$osDiskId = $vm.properties.storageProfile.osDisk.managedDisk.id

Write-Host "OS Disk ID: $osDiskId"

# 2b) Request SAS URL for exporting the disk
$diskName = ($osDiskId.Split("/")[-1])
$exportUri = "https://management.azure.com$osDiskId/beginGetAccess?api-version=2023-04-02"

$exportBody = @{
    access = "Read"
    durationInSeconds = 3600
} | ConvertTo-Json

Write-Host "Requesting SAS URL..."
$exportResponse = Invoke-RestMethod -Method Post -Uri $exportUri -Headers $headers -Body $exportBody -ContentType "application/json"

$sasUrl = $exportResponse.accessSAS
Write-Host "SAS URL received."

# -------------------------------
# 3) DOWNLOAD THE OS DISK VHD
# -------------------------------
Write-Host "Downloading OS Disk VHD... this may take a while."

Invoke-WebRequest -Uri $sasUrl -OutFile $outputVhdPath

Write-Host "Download complete: $outputVhdPath"
