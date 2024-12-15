import unittest
import json
import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aact_openhands.app import app

class TestFlaskEndpoints(unittest.TestCase):
    """Test Flask server endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')

    def test_run_dataflow_lifecycle(self):
        """Test complete dataflow lifecycle"""
        # Test starting a process
        response = self.app.post('/run-dataflow')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'started')

        # Test getting initial status
        status_response = self.app.get('/status')
        self.assertEqual(status_response.status_code, 200)
        status_data = json.loads(status_response.data)
        self.assertEqual(status_data['status'], 'running')
        self.assertIsNone(status_data['output'])
        self.assertIsNone(status_data['success'])

        # Test starting a new process while one is running
        second_response = self.app.post('/run-dataflow')
        self.assertEqual(second_response.status_code, 200)
        second_data = json.loads(second_response.data)
        self.assertEqual(second_data['status'], 'started')

if __name__ == '__main__':
    unittest.main() 