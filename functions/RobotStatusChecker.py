import requests
from PyQt6.QtCore import QThread, pyqtSignal
import time


class RobotStatusChecker(QThread):
    """Background thread to check robot status asynchronously"""
    status_changed = pyqtSignal(str)  # Emits "Online" or "Offline"
    
    def __init__(self, robot_url="http://10.91.170.213/status", check_interval=5):
        super().__init__()
        self.robot_url = robot_url
        self.check_interval = check_interval  # Check every N seconds
        self.running = True
        self.daemon = True
    
    def run(self):
        """Run the status checking loop"""
        while self.running:
            try:
                # Try to send a status request to the robot
                response = requests.get(self.robot_url, timeout=3)
                if response.status_code == 200:
                    self.status_changed.emit("Online")
                else:
                    self.status_changed.emit("Offline")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Robot not reachable
                self.status_changed.emit("Offline")
            except Exception as e:
                print(f"Error checking robot status: {e}")
                self.status_changed.emit("Offline")
            
            # Wait before next check
            time.sleep(self.check_interval)
    
    def stop(self):
        """Stop the checking thread"""
        self.running = False
        self.wait()  # Wait for thread to finish
