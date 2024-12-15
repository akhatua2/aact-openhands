#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup processes
cleanup() {
    echo -e "\n${GREEN}Cleaning up...${NC}"
    if [ ! -z "$SERVER_PID" ]; then
        kill -9 $SERVER_PID 2>/dev/null || true
    fi
    rm -f server.log test_config.toml temp_config.toml 2>/dev/null
}

# Set trap for cleanup
trap cleanup EXIT

echo "Running Flask server tests..."

# Cleanup any existing Flask processes
echo -e "\n${GREEN}Cleaning up existing processes...${NC}"
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Run unit tests
echo -e "\n${GREEN}Running unit tests...${NC}"
poetry run python test_server.py -v

# Start the Flask server in the background
echo -e "\n${GREEN}Starting Flask server...${NC}"
poetry run python app.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start and verify it's running
echo "Waiting for server to start..."
for i in {1..10}; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "Server is up!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}Server failed to start${NC}"
        cat server.log
        exit 1
    fi
    echo "Attempt $i: Server not ready yet..."
    sleep 1
done

# Run live server tests
echo -e "\n${GREEN}Running live server tests...${NC}"
poetry run python test_live_server.py
TEST_EXIT_CODE=$?

# On failure, show server logs
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo -e "\n${RED}Test failed. Server logs:${NC}"
    cat server.log
fi

exit $TEST_EXIT_CODE