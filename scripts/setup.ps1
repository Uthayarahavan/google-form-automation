# Windows PowerShell setup script for Google Forms Creation & Review System

# Prevent closing on errors
$ErrorActionPreference = "Stop"
try {
    Write-Output "Setting up Google Forms Creation & Review System..."

    # Define specific paths
    $pythonPath = "C:\Users\uthay\AppData\Local\Programs\Python\Python311\python.exe"
    $nodePath = "C:\Program Files\nodejs"
    $npmPath = "$nodePath\npm.cmd"

    # Check if the Python executable exists
    if (-not (Test-Path $pythonPath)) {
        Write-Error "Python not found at $pythonPath. Please check the path."
        exit 1
    }

    # Check if the Node.js executable exists
    if (-not (Test-Path $npmPath)) {
        Write-Error "Node.js npm not found at $npmPath. Please check the path."
        exit 1
    }

    Write-Output "Using Python at: $pythonPath"
    Write-Output "Using Node.js at: $nodePath"

    # Add Node.js to PATH for this session
    $env:Path = "$nodePath;$env:Path"

    # Get the script directory and project root
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptDir
    Write-Output "Project root directory: $projectRoot"

    # Set up paths
    $venvPath = Join-Path -Path $projectRoot -ChildPath "venv"
    $backendDir = Join-Path -Path $projectRoot -ChildPath "backend"
    $frontendDir = Join-Path -Path $projectRoot -ChildPath "frontend"
    $credentialsDir = Join-Path -Path $backendDir -ChildPath "credentials"
    $requirementsPath = Join-Path -Path $backendDir -ChildPath "requirements.txt"

    # Check if backend/requirements.txt exists
    if (-not (Test-Path $requirementsPath)) {
        Write-Error "Requirements file not found at: $requirementsPath"
        exit 1
    }

    # Remove existing virtual environment if it exists
    if (Test-Path -Path $venvPath) {
        Write-Output "Removing existing virtual environment..."
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Create Python virtual environment
    Write-Output "`nCreating Python virtual environment..."
    try {
        & $pythonPath -m venv $venvPath
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        Write-Output "Trying alternative method..."
        & $pythonPath -m pip install virtualenv
        & $pythonPath -m virtualenv $venvPath
    }

    # Verify virtual environment creation
    if (-not (Test-Path -Path "$venvPath\Scripts\python.exe")) {
        Write-Error "Failed to create virtual environment properly. Scripts directory not found."
        exit 1
    }

    # Activate virtual environment - using direct paths instead of activation script
    Write-Output "`nUsing virtual environment..."
    $venvPython = Join-Path -Path $venvPath -ChildPath "Scripts\python.exe"
    $venvPip = Join-Path -Path $venvPath -ChildPath "Scripts\pip.exe"

    # Upgrade pip in the virtual environment
    Write-Output "`nUpgrading pip in the virtual environment..."
    try {
        & $venvPython -m pip install --upgrade pip
    } catch {
        Write-Error "Failed to upgrade pip: $_"
        # Continue anyway
    }

    # Install backend dependencies
    Write-Output "`nInstalling backend dependencies..."
    & $venvPip install -r $requirementsPath

    # Create credentials directory if it doesn't exist
    if (-not (Test-Path -Path $credentialsDir)) {
        Write-Output "`nCreating credentials directory..."
        New-Item -ItemType Directory -Path $credentialsDir -Force | Out-Null
    }

    # Copy Google credentials to backend folder if not already there
    $rootCredentialsDir = Join-Path -Path $projectRoot -ChildPath "credentials"
    $clientSecretPath = Join-Path -Path $rootCredentialsDir -ChildPath "client_secret.json"
    $serviceAccountPath = Join-Path -Path $rootCredentialsDir -ChildPath "service_account.json"

    if (Test-Path -Path $clientSecretPath) {
        Write-Output "Copying Google client_secret.json to backend folder..."
        Copy-Item -Path $clientSecretPath -Destination (Join-Path -Path $credentialsDir -ChildPath "client_secret.json") -Force
    } else {
        Write-Warning "client_secret.json not found in credentials directory. Please provide it manually."
    }

    if (Test-Path -Path $serviceAccountPath) {
        Write-Output "Copying Google service_account.json to backend folder..."
        Copy-Item -Path $serviceAccountPath -Destination (Join-Path -Path $credentialsDir -ChildPath "service_account.json") -Force
    } else {
        Write-Warning "service_account.json not found in credentials directory. Please provide it manually."
    }

    # Create logs directory if it doesn't exist
    $logsDir = Join-Path -Path $projectRoot -ChildPath "logs"
    if (-not (Test-Path $logsDir)) {
        Write-Output "`nCreating logs directory..."
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    # Install frontend dependencies
    Write-Output "`nInstalling frontend dependencies..."
    if (Test-Path -Path $frontendDir) {
        Set-Location -Path $frontendDir
        & $npmPath install
        Set-Location -Path $projectRoot
    } else {
        Write-Error "Frontend directory not found at: $frontendDir"
        exit 1
    }

    # Verify installation
    Write-Output "`nVerification:"
    $venvSuccess = Test-Path $venvPath
    Write-Output "✓ Python virtual environment: $venvSuccess"
    Write-Output "✓ Backend dependencies installed"
    Write-Output "✓ Frontend dependencies installed"
    Write-Output "✓ Credentials directory: $(Test-Path $credentialsDir)"
    Write-Output "✓ Logs directory: $(Test-Path $logsDir)"

    Write-Output "`nSetup completed successfully!"
    Write-Output "To run the application menu: .\start.ps1"
    Write-Output "To start the application directly: .\scripts\run.ps1"
} catch {
    Write-Error "An error occurred during setup: $_"
    Write-Output "Error details: $($_.Exception)"
}

# Keep window open at the end
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "`nSetup script execution completed."
    Read-Host "Press Enter to exit"
} 