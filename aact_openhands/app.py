from flask import Flask, jsonify, request
import subprocess
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any
from aact_openhands.utils import AgentAction, ActionType
from aact.messages import Text
from openhands.events.action import (
    BrowseURLAction,
    CmdRunAction,
    FileWriteAction,
    FileReadAction,
    BrowseInteractiveAction,
)

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
        self.runtime = None

    def _create_action(self, observation: AgentAction) -> Any:
        """
        Creates an action based on the observation's action type.
        
        Args:
            observation (AgentAction): The observation containing 
            the action type and arguments.
            
        Returns:
            Any: The created action object
        """
        action_type = observation.action_type
        argument = observation.argument
        path = observation.path

        if action_type == ActionType.BROWSE:
            return BrowseURLAction(url=argument)
        elif action_type == ActionType.BROWSE_ACTION:
            return BrowseInteractiveAction(browser_actions=argument)
        elif action_type == ActionType.RUN:
            return CmdRunAction(command=argument)
        elif action_type == ActionType.WRITE:
            if path is None:
                raise ValueError("Path cannot be None for WRITE action")
            return FileWriteAction(path=path, content=argument)
        elif action_type == ActionType.READ:
            if path is None:
                raise ValueError("Path cannot be None for READ action")
            return FileReadAction(path=path)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    def execute_action(self, action: AgentAction) -> Optional[str]:
        """
        Execute an action and return its result.
        
        Args:
            action (AgentAction): The action to execute
            
        Returns:
            Optional[str]: The result of the action or None if runtime not available
        """
        try:
            action_obj = self._create_action(action)
            # For testing, just return a string representation
            return str(action_obj)
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            raise

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

@app.route('/action', methods=['POST'])
def handle_action():
    """Handle different types of actions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        action = AgentAction(
            agent_name=data.get('agent_name', 'default'),
            action_type=ActionType(data.get('action_type')),
            argument=data.get('argument', ''),
            path=data.get('path')
        )
        
        result = process_manager.execute_action(action)
        if result is None:
            return jsonify({'status': 'error', 'error': 'Runtime not available'}), 503
            
        # Convert result to Text object
        text_result = Text(text=str(result))
        
        response: Dict[str, Any] = {
            'status': 'success',
            'action_type': str(action.action_type),
            'result': text_result.text
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({'status': 'error', 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error handling action: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        process_manager.stop()