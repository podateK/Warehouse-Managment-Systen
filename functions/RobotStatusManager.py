from PyQt6.QtCore import QObject, pyqtSignal
from functions.RobotStatusChecker import RobotStatusChecker
from functions.ConfigManager import ConfigManager
from functions.RequestSender import RequestSender
import requests
import json


class RobotStatusManager(QObject):
    
    status_changed = pyqtSignal(str)
    drive_mode_changed = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._status = "Offline"
        self._drive_mode = "AUTOMATIC"
        self._checker = None
        self._request_sender = RequestSender()
        self._initialized = True
        print("✓ RobotStatusManager initialized", flush=True)
    
    def start(self):
        """Start the robot status checker"""
        if self._checker is not None:
            return
        
        print("📡 Starting RobotStatusChecker...", flush=True)
        self._checker = RobotStatusChecker()
        self._checker.status_changed.connect(self._on_status_changed)
        self._checker.start()
    
    def _on_status_changed(self, status):
        """Internal handler for status changes"""
        if self._status != status:
            print(f"🔄 Status changed: {self._status} → {status}", flush=True)
            self._status = status
            self.status_changed.emit(status)

    def refresh_now(self):
        """Force immediate status refresh"""
        try:
            robot_url = ConfigManager.get_robot_base_url()
            timeout = ConfigManager.get_robot_timeout()
            
            print(f"🔍 DEBUG: robot_url = {robot_url}", flush=True)
            print(f"🔍 DEBUG: timeout = {timeout}", flush=True)
            print(f"🔍 DEBUG: Sending request...", flush=True)
            
            response = requests.get(robot_url, timeout=timeout)
            
            print(f"🔍 DEBUG: Response status code = {response.status_code}", flush=True)
            
            status = "Online" if response.status_code == 200 else "Offline"
        except requests.exceptions.Timeout as e:
            print(f"❌ TIMEOUT: {e}", flush=True)
            status = "Offline"
        except requests.exceptions.ConnectionError as e:
            print(f"❌ CONNECTION ERROR: {e}", flush=True)
            status = "Offline"
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}", flush=True)
            status = "Offline"
        
        self._on_status_changed(status)
        return status

    def refresh_now_with_details(self):
        """Force immediate status refresh with details"""
        robot_url = ConfigManager.get_robot_base_url()
        timeout = ConfigManager.get_robot_timeout()
        
        request_data = {
            "method": "GET",
            "url": robot_url,
            "timeout": timeout,
        }

        try:
            response = requests.get(robot_url, timeout=timeout)
            status = "Online" if response.status_code == 200 else "Offline"
            response_data = {
                "status_code": response.status_code,
                "body": response.text or "Empty response",
            }
        except requests.exceptions.Timeout as e:
            status = "Offline"
            response_data = {
                "status_code": None,
                "body": f"Timeout: {str(e)}",
            }
        except requests.exceptions.ConnectionError as e:
            status = "Offline"
            response_data = {
                "status_code": None,
                "body": f"Connection error: {str(e)}",
            }
        except Exception as e:
            status = "Offline"
            response_data = {
                "status_code": None,
                "body": str(e),
            }

        details = {
            "request": request_data,
            "response": response_data,
            "status": status,
        }

        print(f"📡 ROBOT CHECK: {json.dumps(details, ensure_ascii=False)}", flush=True)
        self._on_status_changed(status)
        return details
    
    def get_status(self):
        """Get current robot status"""
        return self._status
    
    def is_online(self):
        """Check if robot is online"""
        return self._status == "Online"

    def get_drive_mode(self):
        """Get current drive mode"""
        return self._drive_mode

    def is_manual_mode(self):
        """Check if manual mode is enabled"""
        return self._drive_mode == "MANUAL"

    def set_manual_mode(self, enabled):
        """Set drive mode and notify robot"""
        mode = "MANUAL" if enabled else "AUTOMATIC"
        
        if self._drive_mode == mode:
            return True, f"Mode already {mode}"

        self._drive_mode = mode
        self.drive_mode_changed.emit(mode)

        mode_payload = {"command": "MODE", "mode": mode}
        success, message = self._request_sender.send_json(mode_payload)
        print(f"🔧 Mode set to {mode}: {message}", flush=True)
        return success, message

    def set_automatic_mode_local(self):
        """Set automatic mode locally"""
        self._drive_mode = "AUTOMATIC"
        self.drive_mode_changed.emit(self._drive_mode)
    
    def stop(self):
        """Stop the checker"""
        if self._checker:
            print("⏹ Stopping RobotStatusChecker...", flush=True)
            self._checker.stop()