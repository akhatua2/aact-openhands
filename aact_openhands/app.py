from flask import Flask, request, jsonify
import subprocess
import os
from dotenv import load_dotenv
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

# Default TOML configuration
DEFAULT_CONFIG = """redis_url = "redis://localhost:6379/0"
extra_modules = ["aact_openhands.openhands_node"]

[[nodes]]
node_name = "runtime"
node_class = "openhands"

[nodes.node_args]
output_channels = ["Runtime:Agent"]
input_channels = ["Agent:Runtime"]
modal_session_id = "arpan"
"""

class AACTProcess:
    def __init__(self):
        self.status = None
        self.output = None
        self.success = None
        self._process = None
        self._config_path = 'temp_config.toml'

    def start(self):
        """Start the AACT process"""
        try:
            # Write config
            with open(self._config_path, 'w') as f:
                f.write(DEFAULT_CONFIG)

            # Start process
            self._process = subprocess.Popen(
                ['poetry', 'run', 'aact', 'run-dataflow', self._config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            self.status = 'running'
            return True
            
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            self.status = 'error'
            self.output = str(e)
            self.success = False
            return False

    def stop(self):
        """Stop the AACT process"""
        if self._process:
            # Close any open streams
            if self._process.stdout:
                self._process.stdout.close()
            if self._process.stderr:
                self._process.stderr.close()
                
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()  # Ensure process is fully cleaned up
            
            self._process = None
        
        if os.path.exists(self._config_path):
            os.remove(self._config_path)

    def get_status(self):
        """Get current process status"""
        if not self._process:
            return {
                'status': self.status or 'not_started',
                'output': self.output,
                'success': self.success
            }

        # Check if process is still running
        if self._process.poll() is None:
            return {
                'status': 'running',
                'output': None,
                'success': None
            }
        
        # Process finished - read output and close streams
        stdout, stderr = self._process.communicate()
        success = self._process.returncode == 0
        
        # Close streams explicitly
        if self._process.stdout:
            self._process.stdout.close()
        if self._process.stderr:
            self._process.stderr.close()
            
        return {
            'status': 'completed',
            'output': stdout if success else stderr,
            'success': success
        }

    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.stop()

# Global process manager
process_manager = AACTProcess()

@app.route('/run-dataflow', methods=['POST'])
def run_dataflow():
    """Start the AACT dataflow process"""
    try:
        # Stop any existing process
        process_manager.stop()
        
        # Start new process
        if process_manager.start():
            return jsonify({'status': 'started'})
        else:
            return jsonify({
                'status': 'error',
                'error': process_manager.output
            }), 500
            
    except Exception as e:
        logger.error(f"Error in run_dataflow: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current process status"""
    return jsonify(process_manager.get_status())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        process_manager.stop()