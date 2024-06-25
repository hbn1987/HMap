#!/bin/bash

# Path to the Python script
SCRIPT="runner.py"

# Generate the log file name with the current date
LOG_FILE="runner_$(date +%Y_%m_%d).log"

# Check if the script exists
if [ ! -f "$SCRIPT" ]; then
    echo "Error: $SCRIPT not found!"
    exit 1
fi

# Run the Python script with nohup and unbuffered output
nohup python3 -u $SCRIPT > "$LOG_FILE" 2>&1 &

# Get the process ID of the last background command
PID=$!

# Print the process ID
echo "Runner started with PID $PID"
