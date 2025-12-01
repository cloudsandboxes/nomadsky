# -------------------------------
# VARIABLES
# -------------------------------
$region        = "eu-west-1"
$instanceId    = "<INSTANCE_ID>"
$bucketName    = "<S3_BUCKET>"
$outputVhdPath = "C:\Temp\osdisk.vhd"

# AWS credentials (from profile or manually)
$awsCreds = Get-AWSCredential -ProfileName default

# Helper: Signed REST call (SigV4)
function Invoke-AWSSignedRest {
    param(
        [string]$Method,
        [string]$Uri,
        [string]$Region,
        [string]$Service = "ec2",
        [string]$Body = ""
    )

    $headers = @{
        "Content-Type" = "application/x-www-form-urlencoded; charset=utf-8"
    }

    $signed = New-AWSPowerShellSession | 
        Add-AWSAuthenticationHeaders -Method $Method -Uri $Uri -Region $Region -Service $Service -Headers $headers -Body $Body -Credentials $awsCreds

    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $signed -Body $Body
}

# -------------------------------
# 1) STOP THE INSTANCE
# -------------------------------
Write-Host "Stopping instance..."
$stopBody = "Action=StopInstances&InstanceId.1=$instanceId&Version=2016-11-15"
Invoke-AWSSignedRest -Method Post -Uri "https://ec2.$region.amazonaws.com/" -Region $region -Body $stopBody

Start-Sleep -Seconds 25

# -------------------------------
# 2) CREATE AMI (Snapshot of root volume)
# -------------------------------
Write-Host "Creating AMI snapshot..."
$amiName = "ExportAMI-$(Get-Date -Format yyyyMMddHHmmss)"
$createAmiBody = "Action=CreateImage&InstanceId=$instanceId&Name=$amiName&Version=2016-11-15"
$amiResponse = Invoke-AWSSignedRest -Method Post -Uri "https://ec2.$region.amazonaws.com/" -Region $region -Body $createAmiBody

$amiId = $amiResponse.CreateImageResponse.CreateImageResult.imageId
Write-Host "AMI created: $amiId"

# Wait for snapshot to finish
Start-Sleep -Seconds 60

# -------------------------------
# 3) EXPORT THE AMI TO S3 AS VHD
# -------------------------------
Write-Host "Creating export task..."

$exportBody = @"
Action=CreateInstanceExportTask
&InstanceId=$instanceId
&Description=OSDiskExport
&ExportToS3Task.DiskImageFormat=vhd
&ExportToS3Task.S3Bucket=$bucketName
&TargetEnvironment=vmware
&Version=2016-11-15
"@

$exportResponse = Invoke-AWSSignedRest -Method Post -Uri "https://ec2.$region.amazonaws.com/" -Region $region -Body $exportBody

$exportTaskId = $exportResponse.CreateInstanceExportTaskResponse.CreateInstanceExportTaskResult.ExportTask.ExportTaskId
Write-Host "Export task started: $exportTaskId"

Write-Host "Waiting for export to finish (5–20 minutes)..."
Start-Sleep -Seconds 300

# -------------------------------
# 4) DOWNLOAD THE EXPORTED VHD FROM S3
# -------------------------------
Write-Host "Downloading VHD from S3..."

# Find object key (export always lands in: exports/instanceId/*.vhd)
$key = "exports/$instanceId/"

# Get first .vhd in the export folder
$objects = Get-S3Object -BucketName $bucketName -KeyPrefix $key
$vhdKey = ($objects | Where-Object { $_.Key -like "*.vhd" }).Key

Read-S3Object -BucketName $bucketName -Key $vhdKey -File $outputVhdPath

Write-Host "Download complete: $outputVhdPath"

