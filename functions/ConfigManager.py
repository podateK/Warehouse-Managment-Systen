import json
import os

class ConfigManager:
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    @staticmethod
    def load_config():
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        try:
            with open(config_path, 'r') as f:
                ConfigManager._config = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found at {config_path}")
            ConfigManager._config = ConfigManager._get_default_config()
        except json.JSONDecodeError:
            print("Error parsing config.json")
            ConfigManager._config = ConfigManager._get_default_config()
    
    @staticmethod
    def _get_default_config():
        return {
            "robot": {
                "ip": "192.168.18.217",
                "port": 5000,
                "status_endpoint": "/status",
                "command_endpoint": "/cmd",
                "timeout": 2,
                "check_interval": 5
            },
            "api": {
                "base_url": "http://192.168.18.52"
            },
            "database": {
                "name": "wms_database.db"
            },
            "ui": {
                "theme": "dark",
                "fullscreen": True
            }
        }
    
    @classmethod
    def get(cls, key_path):
        if cls._config is None:
            cls.load_config()
        
        keys = key_path.split('.')
        value = cls._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    @classmethod
    def get_robot_url(cls):
        ip = cls.get('robot.ip')
        port = cls.get('robot.port')
        endpoint = cls.get('robot.status_endpoint')
        return f"http://{ip}:{port}{endpoint}"

    @classmethod
    def get_robot_base_url(cls):
        ip = cls.get('robot.ip')
        port = cls.get('robot.port')
        return f"http://{ip}:{port}"
    
    @classmethod
    def get_robot_command_url(cls):
        ip = cls.get('robot.ip')
        port = cls.get('robot.port')
        endpoint = cls.get('robot.command_endpoint')
        return f"http://{ip}:{port}{endpoint}"
    
    @classmethod
    def get_robot_timeout(cls):
        return cls.get('robot.timeout') or 2
    
    @classmethod
    def get_robot_check_interval(cls):
        """Get robot status check interval"""
        return cls.get('robot.check_interval') or 5
