import subprocess
import sys
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AACTCommandTest:
    """Test AACT command functionality"""
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'test_config.toml')
        self.process = None
        
    def setup(self):
        """Set up test configuration"""
        config_content = """redis_url = "redis://localhost:6379/0"
extra_modules = ["aact_openhands.openhands_node"]

[[nodes]]
node_name = "runtime"
node_class = "openhands"

[nodes.node_args]
output_channels = ["Runtime:Agent"]
input_channels = ["Agent:Runtime"]
modal_session_id = "ap"
"""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
            
    def cleanup(self):
        """Clean up resources"""
        if self.process:
            # Close any open streams
            if self.process.stdout:
                self.process.stdout.close()
            if self.process.stderr:
                self.process.stderr.close()
                
            if self.process.poll() is None:
                logger.info("Terminating AACT process...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Process didn't terminate, forcing...")
                    self.process.kill()
                    self.process.wait()  # Ensure process is fully cleaned up
            
            self.process = None
        
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
            
    def run_test(self):
        """Run the integration test"""
        try:
            self.setup()
            
            # Start the AACT process
            logger.info("Starting AACT process...")
            self.process = subprocess.Popen(
                ['poetry', 'run', 'aact', 'run-dataflow', self.config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Wait to see if it starts properly
            time.sleep(2)
            
            # Check if process is running
            if self.process.poll() is None:
                logger.info("Process started successfully and is running")
                print("\n✅ Test passed: AACT command started successfully")
                return True
            else:
                # Process exited early - read output and close streams
                stdout, stderr = self.process.communicate()
                logger.error(f"Process exited early with return code: {self.process.returncode}")
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                print("\n❌ Test failed: Process exited unexpectedly")
                return False
                
        except Exception as e:
            logger.error("Test failed with error", exc_info=True)
            print(f"\n❌ Test failed with error: {str(e)}")
            return False
        finally:
            self.cleanup()
            
    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.cleanup()

def main():
    """Main test runner"""
    print("Testing AACT command...")
    test = AACTCommandTest()
    success = test.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 