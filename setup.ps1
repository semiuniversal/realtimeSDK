<#
.SYNOPSIS
    Setup script for Python project environment using uv sync.

.DESCRIPTION
    Installs 'uv' if missing, sets up project environment using 'uv sync',
    and provides user-friendly messages with multiple usage options.
#>

function Write-Separator {
    Write-Host ('-'*60) -ForegroundColor DarkGray
}

Write-Host "Starting project environment setup..." -ForegroundColor Cyan
Write-Separator

# --- Step 1: Check if 'uv' command exists; install if not ---
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "'uv' command not found. Installing uv..." -ForegroundColor Yellow

    try {
        powershell -ExecutionPolicy ByPass -Command "Invoke-Expression (Invoke-RestMethod https://astral.sh/uv/install.ps1)"
        $uvInstallPath = "$env:USERPROFILE\.local\bin"

        if (-not ($env:PATH -like "*$uvInstallPath*")) {
            $env:PATH = "$uvInstallPath;$env:PATH"
            Write-Host "Temporarily added uv install path to PATH for this session." -ForegroundColor Green
        }

        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
            Write-Host "'uv' was installed but not found in the current shell." -ForegroundColor Yellow
            Write-Host "Please CLOSE and REOPEN your terminal, then rerun this script." -ForegroundColor Cyan
            exit 0
        } else {
            Write-Host "'uv' installed successfully!" -ForegroundColor Green
        }
    }
    catch {
        Write-Error "An error occurred during 'uv' installation: $_"
        Write-Host "Please install 'uv' manually using: irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "'uv' command is already installed." -ForegroundColor Green
}

Write-Separator

# --- Step 2: Preemptively remove existing .venv virtual environment ---
if (Test-Path ".venv") {
    Write-Host "Existing '.venv' directory found. Removing to start fresh..." -ForegroundColor Yellow
    try {
        Remove-Item -Recurse -Force -LiteralPath ".venv"
        Write-Host "Deleted existing '.venv' directory." -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to remove existing '.venv': $_"
        exit 1
    }
} else {
    Write-Host "No existing '.venv' directory found. Proceeding..."
}

Write-Separator

# --- Step 3: Setup project environment using uv sync ---
Write-Host "Setting up project environment using 'uv sync'..." -ForegroundColor Cyan
Write-Host "This will create a virtual environment and install all dependencies..." -ForegroundColor Gray
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Error "Project setup failed. Please check uv installation and pyproject.toml configuration."
    exit 1
}
Write-Host "Project environment set up successfully." -ForegroundColor Green

Write-Separator

# --- Step 4: Verify the installation ---
Write-Host "Verifying installation..." -ForegroundColor Cyan

$pythonExe = ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = ".venv\bin\python"
}

if (Test-Path $pythonExe) {
    Write-Host "Virtual environment created at '.venv\'" -ForegroundColor Green
    $pythonVersion = & $pythonExe --version
    Write-Host "Python interpreter: $pythonVersion" -ForegroundColor Green
    
    # Test the module import
    Write-Host "Testing module import..." -ForegroundColor Gray
    try {
        $testResult = & $pythonExe -c "import realtime_hairbrush; print('✓ realtime_hairbrush imported successfully!')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host $testResult -ForegroundColor Green
            Write-Host "Module verification passed." -ForegroundColor Green
        } else {
            Write-Host "Warning: Module import test failed. Installation may be incomplete." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Warning: Could not test module import." -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: Virtual environment not found at expected location." -ForegroundColor Yellow
}

Write-Separator

# --- Final message ---
Write-Host "Setup complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Your project is ready to use. Choose your preferred workflow:" -ForegroundColor Cyan
Write-Host ""
Write-Host "OPTION 1: Activate the virtual environment (traditional approach):" -ForegroundColor White
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python -c `"import realtime_hairbrush; print('Ready to use!')`"" -ForegroundColor Gray
Write-Host "   # Environment stays active until you run 'deactivate'" -ForegroundColor DarkGray
Write-Host ""
Write-Host "OPTION 2: Use uv run for individual commands (no persistent activation):" -ForegroundColor White
Write-Host "   uv run python -c `"import realtime_hairbrush; print('Ready to use!')`"" -ForegroundColor Gray
Write-Host "   uv run airbrush tui-textual" -ForegroundColor Gray
Write-Host "   # Each command runs in venv but doesn't stay active" -ForegroundColor DarkGray
Write-Host ""
Write-Host "OPTION 3: Use the Python interpreter directly:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\python.exe -c `"import realtime_hairbrush; print('Ready to use!')`"" -ForegroundColor Gray
Write-Host ""
Write-Host "Key differences:" -ForegroundColor Yellow
Write-Host "• Option 1: Activates venv persistently until you deactivate" -ForegroundColor DarkGray
Write-Host "• Option 2: Runs each command in venv but returns to normal shell" -ForegroundColor DarkGray
Write-Host "• Option 3: Direct execution without activation" -ForegroundColor DarkGray
Write-Separator

exit 0