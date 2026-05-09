#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
printf "Starting the server...\n"
source "$SCRIPT_DIR/fileserver/bin/activate"
cd "$SCRIPT_DIR/service"
python3 app.py
exec bash