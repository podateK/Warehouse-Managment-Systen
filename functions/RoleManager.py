
class RoleManager:
    
    ROLES = {
        'admin': {
            'name': 'Administrator',
            'permissions': [
                'view_dashboard', 'edit_documents', 'delete_documents',
                'manage_users', 'view_reports', 'generate_reports',
                'backup_database', 'restore_database', 'view_audit_log',
                'manage_settings', 'robot_control', 'generate_labels',
                'export_data', 'edit_map'
            ]
        },
        'manager': {
            'name': 'Kierownik Magazynu',
            'permissions': [
                'view_dashboard', 'edit_documents', 'manage_users',
                'view_reports', 'generate_reports', 'view_audit_log',
                'robot_control', 'generate_labels', 'export_data',
                'edit_map'
            ]
        },
        'operator': {
            'name': 'Operator Magazynowy',
            'permissions': [
                'view_dashboard', 'edit_documents', 'view_reports',
                'robot_control', 'generate_labels'
            ]
        },
        'viewer': {
            'name': 'Przeglądacz',
            'permissions': [
                'view_dashboard', 'view_reports', 'view_audit_log'
            ]
        }
    }
    
    @classmethod
    def get_role(cls, role_name):
        """Get role by name"""
        return cls.ROLES.get(role_name, None)
    
    @classmethod
    def get_permissions(cls, role_name):
        """Get permissions for a role"""
        role = cls.get_role(role_name)
        return role['permissions'] if role else []
    
    @classmethod
    def has_permission(cls, role_name, permission):
        """Check if role has specific permission"""
        permissions = cls.get_permissions(role_name)
        return permission in permissions
    
    @classmethod
    def get_all_roles(cls):
        """Get all available roles"""
        return {k: v['name'] for k, v in cls.ROLES.items()}
    
    @classmethod
    def get_role_display_name(cls, role_name):
        """Get display name for role"""
        role = cls.get_role(role_name)
        return role['name'] if role else role_name


class UserPermissionChecker:
    """Check user permissions for actions"""
    
    def __init__(self, user_role):
        self.user_role = user_role
        self.permissions = RoleManager.get_permissions(user_role)
    
    def can_view_dashboard(self):
        return RoleManager.has_permission(self.user_role, 'view_dashboard')
    
    def can_edit_documents(self):
        return RoleManager.has_permission(self.user_role, 'edit_documents')
    
    def can_delete_documents(self):
        return RoleManager.has_permission(self.user_role, 'delete_documents')
    
    def can_manage_users(self):
        return RoleManager.has_permission(self.user_role, 'manage_users')
    
    def can_view_reports(self):
        return RoleManager.has_permission(self.user_role, 'view_reports')
    
    def can_generate_reports(self):
        return RoleManager.has_permission(self.user_role, 'generate_reports')
    
    def can_backup_database(self):
        return RoleManager.has_permission(self.user_role, 'backup_database')
    
    def can_restore_database(self):
        return RoleManager.has_permission(self.user_role, 'restore_database')
    
    def can_view_audit_log(self):
        return RoleManager.has_permission(self.user_role, 'view_audit_log')
    
    def can_manage_settings(self):
        return RoleManager.has_permission(self.user_role, 'manage_settings')
    
    def can_control_robot(self):
        return RoleManager.has_permission(self.user_role, 'robot_control')
    
    def can_generate_labels(self):
        return RoleManager.has_permission(self.user_role, 'generate_labels')
    
    def can_export_data(self):
        return RoleManager.has_permission(self.user_role, 'export_data')
    
    def can_edit_map(self):
        return RoleManager.has_permission(self.user_role, 'edit_map')
    
    def check_permission(self, permission):
        """Generic permission check"""
        return RoleManager.has_permission(self.user_role, permission)
