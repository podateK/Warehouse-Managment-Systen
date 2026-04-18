from functions.database_manager import DatabaseManager
from datetime import datetime
import json

class AuditLogger:
    
    EVENT_TYPES = {
        'LOGIN': 'Logowanie',
        'LOGOUT': 'Wylogowanie',
        'USER_CREATE': 'Utworzenie użytkownika',
        'USER_DELETE': 'Usunięcie użytkownika',
        'USER_UPDATE': 'Zmiana użytkownika',
        'DOCUMENT_CREATE': 'Utworzenie dokumentu',
        'DOCUMENT_DELETE': 'Usunięcie dokumentu',
        'DOCUMENT_MODIFY': 'Modyfikacja dokumentu',
        'PDF_GENERATE': 'Generacja PDF',
        'LABEL_GENERATE': 'Generacja etykiety',
        'REPORT_GENERATE': 'Generacja raportu',
        'ROBOT_COMMAND': 'Polecenie robota',
        'ROBOT_STATUS': 'Zmiana statusu robota',
        'CONFIG_CHANGE': 'Zmiana konfiguracji',
        'BACKUP_CREATE': 'Utworzenie kopii zapasowej',
        'BACKUP_RESTORE': 'Przywrócenie kopii zapasowej',
        'SYSTEM_ERROR': 'Błąd systemu',
        'SECURITY_EVENT': 'Zdarzenie bezpieczeństwa',
    }
    
    LOG_LEVELS = {
        'INFO': 'INFO',
        'WARNING': 'OSTRZEŻENIE',
        'ERROR': 'BŁĄD',
        'CRITICAL': 'KRYTYCZNE',
    }
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = DatabaseManager()
        return cls._instance
    
    @staticmethod
    def log(event_type, user_id, description, level='INFO', details=None):
        logger = AuditLogger()
        
        timestamp = datetime.now().isoformat()
        event_name = AuditLogger.EVENT_TYPES.get(event_type, event_type)
        level_name = AuditLogger.LOG_LEVELS.get(level, 'INFO')
        
        details_json = json.dumps(details) if details else None
        
        try:
            logger.db.execute("""
                INSERT INTO audit_log 
                (timestamp, event_type, user_id, description, level, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, event_type, user_id, description, level_name, details_json))
            logger.db.commit()
        except Exception as e:
            print(f"[AUDIT] Error logging event: {str(e)}")
    
    @staticmethod
    def get_logs(limit=1000):
        logger = AuditLogger()
        try:
            logs = logger.db.execute("""
                SELECT timestamp, event_type, user_id, description, level
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return logs
        except:
            return []
    
    @staticmethod
    def get_user_logs(user_id, limit=500):
        logger = AuditLogger()
        try:
            logs = logger.db.execute("""
                SELECT timestamp, event_type, user_id, description, level
                FROM audit_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
            return logs
        except:
            return []
    
    @staticmethod
    def get_logs_by_type(event_type, limit=500):
        """Get logs for specific event type"""
        logger = AuditLogger()
        try:
            logs = logger.db.execute("""
                SELECT timestamp, event_type, user_id, description, level
                FROM audit_log
                WHERE event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (event_type, limit)).fetchall()
            return logs
        except:
            return []
    
    @staticmethod
    def get_security_events(limit=500):
        """Get all security events"""
        logger = AuditLogger()
        try:
            logs = logger.db.execute("""
                SELECT timestamp, event_type, user_id, description, level
                FROM audit_log
                WHERE level IN ('ERROR', 'CRITICAL', 'OSTRZEŻENIE', 'KRYTYCZNE')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return logs
        except:
            return []
