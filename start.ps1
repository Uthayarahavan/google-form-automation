# Google Forms Creation & Review System - Quick Start Menu
# This script provides a simple way to run the application or response sharing tools

# Keep window open on errors
$ErrorActionPreference = "Stop"
try {
    # Set specific paths
    $PYTHON_PATH = "C:\Users\uthay\AppData\Local\Programs\Python\Python311\python.exe"
    $NODE_PATH = "C:\Program Files\nodejs"
    $NPM_PATH = "$NODE_PATH\npm.cmd"

    function Show-Menu {
        Clear-Host
        Write-Host "================= Google Forms Creation & Review System ================="
        Write-Host "1. Start Application (Backend & Frontend)"
        Write-Host "2. Generate Response URLs"
        Write-Host "3. Enable Response Sharing for All Forms"
        Write-Host "4. Share Existing Forms with Another Account"
        Write-Host "5. Stop Application (Kill Running Processes)"
        Write-Host "6. Open Application in Browser"
        Write-Host "Q. Quit"
        Write-Host "========================================================================"
    }

    function Stop-ApplicationProcesses {
        Write-Host "Stopping running processes..."
        
        # Stop Python processes (backend)
        Get-Process -Name python* -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "Stopping Python process: $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        
        # Stop Node processes (frontend)
        Get-Process -Name node* -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "Stopping Node process: $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "All application processes stopped."
    }

    function Start-Application {
        Write-Host "Starting application..."
        
        # Verify paths exist
        if (-not (Test-Path $PYTHON_PATH)) {
            Write-Error "Python not found at: $PYTHON_PATH"
            return
        }
        
        if (-not (Test-Path $NPM_PATH)) {
            Write-Error "Node.js npm not found at: $NPM_PATH"
            return
        }
        
        # First stop any existing processes to avoid port conflicts
        Write-Host "Stopping any existing processes to avoid port conflicts..."
        Stop-ApplicationProcesses
        
        # Give processes time to fully terminate
        Start-Sleep -Seconds 3
        
        # Add Node.js to PATH for this session
        $env:Path = "$NODE_PATH;$env:Path"
        
        # Now start the application
        & ".\scripts\run.ps1"
    }

    function Activate-Environment {
        # Ensure virtual environment exists
        $venvPath = Join-Path -Path (Get-Location) -ChildPath "venv"
        if (-not (Test-Path -Path "$venvPath\Scripts\activate.ps1")) {
            Write-Host "Creating virtual environment..."
            & $PYTHON_PATH -m venv $venvPath
        }
        
        # Return the Python executable path in the virtual environment
        return Join-Path -Path $venvPath -ChildPath "Scripts\python.exe"
    }

    function Generate-ResponseUrls {
        Write-Host "Generating response URLs..."
        $pythonExe = Activate-Environment
        if (Test-Path $pythonExe) {
            & $pythonExe ".\share_response_urls.py"
        } else {
            Write-Error "Python virtual environment not found."
        }
        Read-Host "`nPress Enter to return to menu"
    }

    function Enable-ResponseSharing {
        Write-Host "Enabling response sharing for all forms..."
        $pythonExe = Activate-Environment
        if (Test-Path $pythonExe) {
            & $pythonExe ".\enable_response_sharing.py"
        } else {
            Write-Error "Python virtual environment not found."
        }
        Read-Host "`nPress Enter to return to menu"
    }

    function Share-ExistingForms {
        Write-Host "Sharing existing forms with another account..."
        $pythonExe = Activate-Environment
        if (Test-Path $pythonExe) {
            & $pythonExe ".\share_existing_forms.py"
        } else {
            Write-Error "Python virtual environment not found."
        }
        Read-Host "`nPress Enter to return to menu"
    }

    function Open-ApplicationInBrowser {
        $frontendUrl = "http://localhost:3000"
        $backendUrl = "http://localhost:8000"
        
        Write-Host "Opening application in browser..."
        Start-Process $frontendUrl
        
        # Ask if they want to open the API docs too
        $openBackend = Read-Host "Do you want to open the API documentation as well? (y/n)"
        if ($openBackend -eq "y" -or $openBackend -eq "Y") {
            Start-Process "$backendUrl/docs"
        }
        
        Read-Host "`nPress Enter to return to menu"
    }

    # Main loop
    $choice = ""
    while ($choice -ne "Q") {
        Show-Menu
        $choice = Read-Host "Please make a selection"
        
        switch ($choice) {
            "1" { Start-Application; break }
            "2" { Generate-ResponseUrls }
            "3" { Enable-ResponseSharing }
            "4" { Share-ExistingForms }
            "5" { Stop-ApplicationProcesses; Read-Host "`nPress Enter to return to menu" }
            "6" { Open-ApplicationInBrowser }
            "Q" { Write-Host "Exiting..."; break }
            "q" { Write-Host "Exiting..."; break }
            default { Write-Host "Invalid option, please try again." -ForegroundColor Red; Start-Sleep -s 1 }
        }
    }
} catch {
    Write-Error "An error occurred: $_"
    Write-Host "Error details: $($_.Exception)"
    Read-Host "Press Enter to exit"
}

# Keep window open at the end
if ($host.Name -eq 'ConsoleHost') {
    Write-Host "Script execution completed."
    Read-Host "Press Enter to exit"
} 