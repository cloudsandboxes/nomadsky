<#
===============================================================================
FUNCTION TEMPLATE — AI & VIBE CODER FRIENDLY
===============================================================================
WHAT THIS FUNCTION DOES
-----------------------
Installs Python, GIT and GITHUB repo on a new VM. 

Prompt:
I need a powershell script that downloads Python and git to a windows server and then clone an existing github repo.  This programs should be installed on a good location, so they could be used by the github code.

PARAMETERS (INPUT)
------------------
$GithubRepoUrl = the URL of NomadSky code.
$CloneDirectory = location on server to install the source code. 

EXPECTED OUTPUT
---------------
- A server running the software. 

LOGGING POLICY
--------------

Remarks
--------------
PowerShell script to install Python, Git, and clone a GitHub repository
Run this script as Administrator

Troubleshoot actions
------------------
Check if python is installed:
Check if git is installed:
Check if repo is installed:
Check error logs:

===============================================================================
#>
param(
    [string]$GithubRepoUrl = "https://github.com/cloudsandboxes/nomadsky.git",
    [string]$CloneDirectory = "C:\Projects"
)

# Configuration
$PythonVersion = "3.12.1"
$PythonInstallPath = "C:\Program Files\Python312"
$GitInstallPath = "C:\Program Files\Git"
$TempDir = "$env:TEMP\DevToolsInstall"

# Create temp directory
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Write-Host "=== Starting installation process ===" -ForegroundColor Green

# Function to add to PATH if not already present
function Add-ToPath {
    param([string]$PathToAdd)
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$PathToAdd*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$PathToAdd",
            "Machine"
        )
        Write-Host "Added $PathToAdd to system PATH" -ForegroundColor Yellow
    }
}

# Install Python
Write-Host "`n[1/3] Installing Python..." -ForegroundColor Cyan
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
$PythonInstaller = "$TempDir\python-installer.exe"

try {
    Write-Host "Downloading Python $PythonVersion..."
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstaller -UseBasicParsing
    
    Write-Host "Installing Python to $PythonInstallPath..."
    Start-Process -FilePath $PythonInstaller -ArgumentList @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_test=0",
        "TargetDir=$PythonInstallPath"
    ) -Wait -NoNewWindow
    
    Add-ToPath "$PythonInstallPath"
    Add-ToPath "$PythonInstallPath\Scripts"
    
    Write-Host "Python installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing Python: $_" -ForegroundColor Red
    exit 1
}

# Install Git
Write-Host "`n[2/3] Installing Git..." -ForegroundColor Cyan
$GitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
$GitInstaller = "$TempDir\git-installer.exe"

try {
    Write-Host "Downloading Git..."
    Invoke-WebRequest -Uri $GitUrl -OutFile $GitInstaller -UseBasicParsing
    
    Write-Host "Installing Git to $GitInstallPath..."
    Start-Process -FilePath $GitInstaller -ArgumentList @(
        "/VERYSILENT",
        "/NORESTART",
        "/DIR=$GitInstallPath",
        "/COMPONENTS=icons,ext\shellhere,assoc,assoc_sh"
    ) -Wait -NoNewWindow
    
    Add-ToPath "$GitInstallPath\cmd"
    
    Write-Host "Git installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing Git: $_" -ForegroundColor Red
    exit 1
}

# Refresh environment variables in current session
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Clone GitHub repository
Write-Host "`n[3/3] Cloning GitHub repository..." -ForegroundColor Cyan

if (-not (Test-Path $CloneDirectory)) {
    New-Item -ItemType Directory -Force -Path $CloneDirectory | Out-Null
}

try {
    Set-Location $CloneDirectory
    
    # Extract repo name from URL
    $RepoName = ($GithubRepoUrl -split '/')[-1] -replace '\.git$'
    $RepoPath = Join-Path $CloneDirectory $RepoName
    
    if (Test-Path $RepoPath) {
        Write-Host "Repository already exists at $RepoPath" -ForegroundColor Yellow
        Write-Host "Pulling latest changes..."
        Set-Location $RepoPath
        & "$GitInstallPath\cmd\git.exe" pull
    } else {
        Write-Host "Cloning repository to $RepoPath..."
        & "$GitInstallPath\cmd\git.exe" clone $GithubRepoUrl
    }
    
    Write-Host "Repository cloned successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error cloning repository: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host "`nCleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

# Verify installations
Write-Host "`n=== Installation Summary ===" -ForegroundColor Green
Write-Host "Python version:" -NoNewline
& "$PythonInstallPath\python.exe" --version
Write-Host "Git version:" -NoNewline
& "$GitInstallPath\cmd\git.exe" --version
Write-Host "Repository location: $CloneDirectory\$RepoName"

Write-Host "`nInstallation complete! Please restart your PowerShell session for PATH changes to take full effect." -ForegroundColor Green
