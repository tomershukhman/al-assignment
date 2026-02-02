#!/bin/bash

# Port configuration
BACKEND_PORT=8000

# Function to kill process on a specific port
kill_port() {
    local port=$1
    echo "Checking port $port..."
    local pids=$(lsof -ti:$port)
    if [ ! -z "$pids" ]; then
        echo "Killing existing processes using port $port (PIDs: $pids)..."
        # Using -9 to ensure it's killed immediately as requested
        echo "$pids" | xargs kill -9
    else
        echo "Port $port is free."
    fi
}

echo "--- Preparing Development Environment ---"

# Kill existing processes
kill_port $BACKEND_PORT

echo "--- Starting Servers ---"

# Start backend server
echo "Starting Backend on port $BACKEND_PORT..."
# Using 'uv run' as per README
uv run uvicorn backend.main:app --reload --port $BACKEND_PORT &
BACKEND_PID=$!



# Trap signals to kill background processes on exit
cleanup() {
    echo ""
    echo "--- Shutting Down ---"
    kill $BACKEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "Servers are running. Press Ctrl+C to stop."
wait
