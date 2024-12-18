#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup processes
cleanup() {
    echo -e "\n${GREEN}Cleaning up...${NC}"
    pkill -f "python aact_openhands/app.py" || true
    rm -f server.log tests/test_config.toml temp_config.toml 2>/dev/null
}

# Set trap for cleanup
trap cleanup EXIT

echo -e "${GREEN}Running all tests...${NC}"

# Run unit tests first
echo -e "\n${GREEN}Running unit tests...${NC}"
poetry run python -m pytest aact_openhands/tests/test_server.py -v -s
UNIT_TEST_EXIT_CODE=$?

if [ $UNIT_TEST_EXIT_CODE -ne 0 ]; then
    echo -e "\n${RED}Unit tests failed${NC}"
    exit $UNIT_TEST_EXIT_CODE
fi

# Run live server tests
echo -e "\n${GREEN}Running live server tests...${NC}"
poetry run python -m pytest aact_openhands/tests/test_live_server.py -v -s
LIVE_TEST_EXIT_CODE=$?

if [ $LIVE_TEST_EXIT_CODE -ne 0 ]; then
    echo -e "\n${RED}Live server tests failed${NC}"
    exit $LIVE_TEST_EXIT_CODE
fi

echo -e "\n${GREEN}All tests passed!${NC}"
exit 0