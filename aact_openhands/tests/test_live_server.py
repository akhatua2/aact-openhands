import subprocess
import logging
import time
import requests
import pytest
import json
from aact_openhands.app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    with app.test_client() as client:
        yield client

@pytest.fixture
def live_server():
    """Start the Flask server for testing"""
    port = 5000
    process = subprocess.Popen(
        ['poetry', 'run', 'python', 'aact_openhands/app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield f"http://localhost:{port}"
    
    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

class TestLiveServer:
    """Test AACT command functionality with live server"""
    
    def test_browse_action(self, live_server):
        """Test BROWSE action endpoint"""
        browse_data = {
            'agent_name': 'test_agent',
            'action_type': 'browse',
            'argument': 'https://example.com'
        }
        print(f"\nSending BROWSE request: {json.dumps(browse_data, indent=2)}")
        response = requests.post(
            f"{live_server}/action",
            json=browse_data
        )
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['action_type'] == 'browse'

    def test_run_action(self, live_server):
        """Test RUN action endpoint"""
        run_data = {
            'agent_name': 'test_agent',
            'action_type': 'run',
            'argument': 'ls -la'
        }
        print(f"\nSending RUN request: {json.dumps(run_data, indent=2)}")
        response = requests.post(
            f"{live_server}/action",
            json=run_data
        )
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['action_type'] == 'run'

    def test_write_action(self, live_server):
        """Test WRITE action endpoint"""
        write_data = {
            'agent_name': 'test_agent',
            'action_type': 'write',
            'argument': 'test content',
            'path': 'test.txt'
        }
        print(f"\nSending WRITE request: {json.dumps(write_data, indent=2)}")
        response = requests.post(
            f"{live_server}/action",
            json=write_data
        )
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['action_type'] == 'write'

    def test_read_action(self, live_server):
        """Test READ action endpoint"""
        read_data = {
            'agent_name': 'test_agent',
            'action_type': 'read',
            'path': 'test.txt'
        }
        print(f"\nSending READ request: {json.dumps(read_data, indent=2)}")
        response = requests.post(
            f"{live_server}/action",
            json=read_data
        )
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['action_type'] == 'read'

    def test_invalid_action(self, live_server):
        """Test invalid action type"""
        invalid_data = {
            'agent_name': 'test_agent',
            'action_type': 'invalid_type',
            'argument': 'test'
        }
        print(f"\nSending INVALID request: {json.dumps(invalid_data, indent=2)}")
        response = requests.post(
            f"{live_server}/action",
            json=invalid_data
        )
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 400
        data = response.json()
        assert data['status'] == 'error' 