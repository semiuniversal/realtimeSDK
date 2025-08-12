#!/bin/bash

set -e

separator() {
    printf -- '------------------------------------------------------------\n'
}

echo "Starting project environment setup..."
separator

# --- Detect Operating System ---
OS_TYPE="$(uname -s)"
case "$OS_TYPE" in
    Linux*)     os="Linux";;
    Darwin*)    os="MacOS";;
    CYGWIN*|MINGW*|MSYS*) os="Windows";;
    *)          os="Unknown";;
esac
echo "Detected Operating System: $os"
separator

# --- Check if 'uv' command is available ---
if ! command -v uv >/dev/null 2>&1; then
    echo "'uv' command not found. Installing 'uv' now..."

    # Use curl or wget to install uv
    if command -v curl >/dev/null 2>&1; then
        bash -c "$(curl -fsSL https://astral.sh/uv/install.sh)" || {
            echo "Error: Failed to install 'uv'. Please install manually: https://astral.sh/uv"
            exit 1
        }
    elif command -v wget >/dev/null 2>&1; then
        bash -c "$(wget -qO- https://astral.sh/uv/install.sh)" || {
            echo "Error: Failed to install 'uv'. Please install manually: https://astral.sh/uv"
            exit 1
        }
    else
        echo "Error: Neither curl nor wget found. Please install 'uv' manually: https://astral.sh/uv"
        exit 1
    fi

    UV_INSTALL_PATH="$HOME/.local/bin"

    if [ -d "$UV_INSTALL_PATH" ] && [[ ":$PATH:" != *":$UV_INSTALL_PATH:"* ]]; then
        export PATH="$UV_INSTALL_PATH:$PATH"
        echo "Temporarily added '$UV_INSTALL_PATH' to PATH for this session."
    fi

    if ! command -v uv >/dev/null 2>&1; then
        echo "'uv' was installed but not found in the current shell."
        echo "Please CLOSE and REOPEN your terminal or run:"
        echo "  export PATH=\"$UV_INSTALL_PATH:\$PATH\""
        echo "Then rerun this script."
        exit 0
    else
        echo "'uv' installed successfully!"
    fi
else
    echo "'uv' command found."
fi

separator

# --- Preemptively remove existing .venv ---
if [ -d ".venv" ]; then
    echo "Existing '.venv' directory found. Removing to start fresh..."
    rm -rf .venv
    echo "Deleted existing '.venv' directory."
else
    echo "No existing '.venv' directory found. Proceeding..."
fi

separator

# --- Setup project environment using uv sync ---
echo "Setting up project environment using 'uv sync'..."
echo "This will create a virtual environment and install all dependencies..."
uv sync || {
    echo "Project setup failed. Please check 'uv' installation and pyproject.toml configuration."
    exit 1
}
echo "Project environment set up successfully."

separator

# --- Verify the installation ---
echo "Verifying installation..."
if [ -f ".venv/bin/python" ]; then
    echo "Virtual environment created at '.venv/'"
    PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
    echo "Python interpreter: $PYTHON_VERSION"
    
    # Test the module import
    echo "Testing module import..."
    if .venv/bin/python -c "import realtime_hairbrush; print('✓ realtime_hairbrush imported successfully!')" 2>/dev/null; then
        echo "Module verification passed."
    else
        echo "Warning: Module import test failed. Installation may be incomplete."
    fi
else
    echo "Warning: Virtual environment not found at expected location."
fi

separator


# --- Final message ---
echo "Setup complete! 🎉"
echo ""
echo "Your project is ready to use. Choose your preferred workflow:"
echo ""
echo "OPTION 1: Activate the virtual environment (traditional approach):"
echo "   source .venv/bin/activate"
echo "   python -c \"import realtime_hairbrush; print('Ready to use!')\""
echo "   # Environment stays active until you run 'deactivate'"
echo ""
echo "OPTION 2: Use uv run for individual commands (no persistent activation):"
echo "   uv run python -c \"import realtime_hairbrush; print('Ready to use!')\""
echo "   uv run airbrush tui-textual"
echo "   # Each command runs in venv but doesn't stay active"
echo ""
echo "OPTION 3: Use the Python interpreter directly:"
echo "   .venv/bin/python -c \"import realtime_hairbrush; print('Ready to use!')\""
echo ""
echo "Key differences:"
echo "• Option 1: Activates venv persistently until you deactivate"
echo "• Option 2: Runs each command in venv but returns to normal shell"
echo "• Option 3: Direct execution without activation"
separator

echo "Suggestion for convenience, if you want to run setup and activate reliably in one command:"
echo "create a bash alias for running setup and activate:"
echo " alias setup='./setup.sh && source .venv/bin/activate'"

separator

exit 0
