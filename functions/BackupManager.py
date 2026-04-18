import shutil
import os
from datetime import datetime
import zipfile
import json

class BackupManager:
    
    BACKUP_DIR = "backups"
    DATABASE_PATH = "wms_database.db"
    
    def __init__(self):
        if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)
    
    def create_backup(self, description=""):
        """
        Create full database backup
        
        Args:
            description (str): Optional backup description
            
        Returns:
            tuple: (backup_path, backup_info_dict)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.BACKUP_DIR, backup_filename)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists(self.DATABASE_PATH):
                    zipf.write(self.DATABASE_PATH, arcname=os.path.basename(self.DATABASE_PATH))
            
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'description': description,
                'filename': backup_filename,
                'size': os.path.getsize(backup_path),
                'database': self.DATABASE_PATH,
            }
            
            metadata_path = backup_path.replace('.zip', '_info.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return backup_path, metadata
            
        except Exception as e:
            raise Exception(f"Błąd tworzenia kopii zapasowej: {str(e)}")
    
    def restore_backup(self, backup_path):
        """
        Restore database from backup
        
        Args:
            backup_path (str): Path to backup file
            
        Returns:
            tuple: (success, message)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Plik kopii zapasowej nie istnieje"
            
            restore_dir = os.path.join(self.BACKUP_DIR, "restore_temp")
            if os.path.exists(restore_dir):
                shutil.rmtree(restore_dir)
            os.makedirs(restore_dir)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_dir)
            
            db_files = [f for f in os.listdir(restore_dir) if f.endswith('.db')]
            
            if not db_files:
                shutil.rmtree(restore_dir)
                return False, "Plik bazy danych nie znaleziony w kopii zapasowej"
            
            if os.path.exists(self.DATABASE_PATH):
                backup_current = f"{self.DATABASE_PATH}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.DATABASE_PATH, backup_current)
            
            restored_db = os.path.join(restore_dir, db_files[0])
            shutil.copy2(restored_db, self.DATABASE_PATH)
            
            shutil.rmtree(restore_dir)
            
            return True, f"Kopia zapasowa przywrócona: {os.path.basename(backup_path)}"
            
        except Exception as e:
            return False, f"Błąd przywracania kopii: {str(e)}"
    
    def get_backups(self):
        """
        Get list of all backups
        
        Returns:
            list: List of backup info dicts
        """
        backups = []
        
        try:
            for filename in sorted(os.listdir(self.BACKUP_DIR)):
                if filename.endswith('_info.json'):
                    info_path = os.path.join(self.BACKUP_DIR, filename)
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        backups.append(info)
        except Exception as e:
            print(f"Błąd odczytywania kopii zapasowych: {str(e)}")
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_backup(self, backup_filename):
        """
        Delete specific backup
        
        Args:
            backup_filename (str): Filename of backup to delete
            
        Returns:
            tuple: (success, message)
        """
        try:
            backup_path = os.path.join(self.BACKUP_DIR, backup_filename)
            info_path = backup_path.replace('.zip', '_info.json')
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
            if os.path.exists(info_path):
                os.remove(info_path)
            
            return True, f"Kopia zapasowa usunięta: {backup_filename}"
            
        except Exception as e:
            return False, f"Błąd usuwania kopii: {str(e)}"
    
    def get_backup_size(self):
        """Get total size of all backups in MB"""
        try:
            total_size = sum(
                os.path.getsize(os.path.join(self.BACKUP_DIR, f))
                for f in os.listdir(self.BACKUP_DIR)
                if f.endswith('.zip')
            )
            return total_size / (1024 * 1024)  # Convert to MB
        except:
            return 0
    
    def auto_backup(self, keep_count=5):
        """
        Create automatic backup and keep only last N backups
        
        Args:
            keep_count (int): Number of backups to keep
            
        Returns:
            tuple: (success, message)
        """
        try:
            backup_path, info = self.create_backup(
                description=f"Automatyczna kopia z {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            backups = self.get_backups()
            if len(backups) > keep_count:
                for backup in backups[keep_count:]:
                    self.delete_backup(backup['filename'])
            
            return True, f"Auto backup: {os.path.basename(backup_path)}"
            
        except Exception as e:
            return False, f"Błąd auto backup: {str(e)}"
