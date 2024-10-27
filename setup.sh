#!/bin/bash

PYTHON_VERSION="3.9"

# Check if Homebrew is installed
if [ ! -x "/opt/homebrew/bin/brew" ]; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    exit 1
fi

/opt/homebrew/bin/brew install tcl-tk
/opt/homebrew/bin/brew upgrade tcl-tk

export LDFLAGS="-L$(/opt/homebrew/bin/brew --prefix tcl-tk)/lib"
export CPPFLAGS="-I$(/opt/homebrew/bin/brew --prefix tcl-tk)/include"
export PKG_CONFIG_PATH="$(/opt/homebrew/bin/brew --prefix tcl-tk)/lib/pkgconfig"

# Check if Python 3.9 is installed via Homebrew
if ! /opt/homebrew/bin/brew list python-tk@$PYTHON_VERSION &>/dev/null; then
    /opt/homebrew/bin/brew install python-tk@3.9
else
    /opt/homebrew/bin/brew reinstall python-tk@3.9

# Use the installed Python 3.9 version from Homebrew to create a virtual environment
PYTHON_PATH="$("/opt/homebrew/bin/brew" --prefix python-tk@3.9)/bin/python3.9"
$PYTHON_PATH -m venv ./venv

# Activate venv and install requirements
source ./venv/bin/activate
pip3.9 install -r requirements.txt