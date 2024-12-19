#!/bin/bash

# Start X server
startx &

# Wait for X server to start
while ! pgrep -x "Xorg" > /dev/null; do
    sleep 1
    echo "Waiting for X server to start..."
done

echo "X server started."

# Environment variable for DISPLAY
export DISPLAY=:0

# Path to the Python script and virtual environment
PYTHON_EXEC="$HOME/Automation_Server/venv/bin/python"
SCRIPT_PATH="$HOME/Automation_Server/src/main.py"

# Infinite loop to restart the script if it crashes
while true; do
    echo "Starting $SCRIPT_PATH..."
    "$PYTHON_EXEC" "$SCRIPT_PATH"

    # Log crash and restart
    echo "$SCRIPT_PATH crashed. Restarting in 5 seconds..."
    sleep 5
done
