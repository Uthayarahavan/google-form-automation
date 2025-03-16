# Windows PowerShell run script for Google Forms Creation & Review System

Write-Output "Starting Google Forms Creation & Review System..."

# Use specific Python path 
$pythonPath = "C:\Users\uthay\AppData\Local\Programs\Python\Python311\python.exe"
# Use specific Node.js path
$nodePath = "C:\Program Files\nodejs"
$npmPath = "$nodePath\npm.cmd"

# Verify Python path
if (-not (Test-Path $pythonPath)) {
    Write-Error "Python not found at: $pythonPath"
    exit 1
}

# Verify Node.js path
if (-not (Test-Path $npmPath)) {
    Write-Error "Node.js npm not found at: $npmPath"
    exit 1
}

Write-Output "Using Python at: $pythonPath"
Write-Output "Using Node.js at: $nodePath"

# Add Node.js to the PATH for this session
$env:Path = "$nodePath;$env:Path"

# Get the script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Write-Output "Project root directory: $projectRoot"

# Set up paths
$venvPath = Join-Path -Path $projectRoot -ChildPath "venv"
$backendDir = Join-Path -Path $projectRoot -ChildPath "backend"
$frontendDir = Join-Path -Path $projectRoot -ChildPath "frontend"
$logsDir = Join-Path -Path $projectRoot -ChildPath "logs"

# Ensure virtual environment exists
if (-not (Test-Path -Path "$venvPath\Scripts\activate.ps1")) {
    Write-Output "Creating virtual environment..."
    & $pythonPath -m venv $venvPath
}

# Activate virtual environment
Write-Output "Activating virtual environment..."
& "$venvPath\Scripts\activate.ps1"

# Check if backend/requirements.txt exists
$requirementsPath = Join-Path -Path $backendDir -ChildPath "requirements.txt"
if (-not (Test-Path $requirementsPath)) {
    Write-Error "Requirements file not found at: $requirementsPath"
    exit 1
}

# Install required packages
Write-Output "Installing required packages..."
& pip install -r $requirementsPath

# Create logs directory if it doesn't exist
if (-not (Test-Path $logsDir)) {
    Write-Output "Creating logs directory..."
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

# Configure backend environment
$envPath = Join-Path -Path $backendDir -ChildPath ".env"
if (Test-Path $envPath) {
    $envContent = Get-Content -Path $envPath
    $envContent = $envContent -replace "DEBUG_MODE=.*", "DEBUG_MODE=True"
    $envContent = $envContent -replace "MOCK_API_CALLS=.*", "MOCK_API_CALLS=False"
    Set-Content -Path $envPath -Value $envContent
    Write-Output "Updated environment variables: DEBUG_MODE=True, MOCK_API_CALLS=False"
}

# Start the backend server
Write-Output "Starting backend server..."
$backendLogPath = Join-Path -Path $logsDir -ChildPath "backend.log"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; & '$venvPath\Scripts\python.exe' run.py 2>&1 | Tee-Object -FilePath '$backendLogPath'"

# Wait for the backend to start
Write-Output "Waiting for backend to start..."
Start-Sleep -Seconds 5

# Start the frontend
Write-Output "Starting frontend server..."
$frontendLogPath = Join-Path -Path $logsDir -ChildPath "frontend.log"
$npmCommand = "cd '$frontendDir'; & '$npmPath' start 2>&1 | Tee-Object -FilePath '$frontendLogPath'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $npmCommand

Write-Output "`nGoogle Forms Creation & Review System is now running!"
Write-Output "Backend server: http://localhost:8000"
Write-Output "Frontend server: http://localhost:3000"
Write-Output "Log files: $logsDir"
Write-Output "`nPress Ctrl+C to stop the script. Close the opened PowerShell windows to stop the servers." 