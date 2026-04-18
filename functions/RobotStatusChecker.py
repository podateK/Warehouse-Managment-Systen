from PyQt6.QtCore import QThread, pyqtSignal
import requests
import time
from functions.ConfigManager import ConfigManager


class RobotStatusChecker(QThread):
    status_changed = pyqtSignal(str)  # Emits "Online" or "Offline"
    
    def __init__(self, robot_url=None, check_interval=None):
        super().__init__()
        self.robot_url = robot_url or ConfigManager.get_robot_base_url()
        self.check_interval = check_interval or ConfigManager.get_robot_check_interval()
        self.running = True
        self.daemon = True

    def run(self):
        """Run the status checking loop"""
        while self.running:
            try:
                timeout = ConfigManager.get_robot_timeout()
                response = requests.get(self.robot_url, timeout=timeout)
                
                if response.status_code == 200:
                    self.status_changed.emit("Online")
                else:
                    self.status_changed.emit("Offline")
                    
            except requests.exceptions.Timeout:
                self.status_changed.emit("Offline")
            except requests.exceptions.ConnectionError:
                self.status_changed.emit("Offline")
            except Exception as e:
                print(f"Error checking robot status: {e}", flush=True)
                self.status_changed.emit("Offline")
            
            time.sleep(self.check_interval)
    
    def stop(self):
        """Stop the checking thread"""
        self.running = False
        self.wait()