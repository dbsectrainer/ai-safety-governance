import typing
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import uuid

@dataclass
class User:
    """Represents a user in the system with role-based access control."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ''
    email: str = ''
    hashed_password: str = ''
    roles: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: typing.Optional[datetime] = None
    is_active: bool = True

class UserManager:
    """Manages user authentication, authorization, and access control."""
    
    def __init__(self, users: typing.Optional[list[User]] = None):
        """
        Initialize UserManager with optional pre-existing users.
        
        :param users: Optional list of initial users
        """
        self._users: dict[str, User] = {}
        self._roles = {
            'admin': ['full_access'],
            'analyst': ['read_monitoring', 'create_reports'],
            'developer': ['read_code', 'run_tests'],
            'security_officer': ['view_security_logs', 'manage_compliance']
        }
        
        if users:
            for user in users:
                self.add_user(user)
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 for secure storage.
        
        :param password: Plain text password
        :return: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_user(self, user: User) -> bool:
        """
        Add a new user to the system.
        
        :param user: User to add
        :return: True if user added successfully, False if username/email exists
        """
        if any(existing.username == user.username or existing.email == user.email 
               for existing in self._users.values()):
            return False
        
        self._users[user.id] = user
        return True
    
    def authenticate(self, username: str, password: str) -> typing.Optional[User]:
        """
        Authenticate a user with username and password.
        
        :param username: User's username
        :param password: User's password
        :return: Authenticated user or None
        """
        for user in self._users.values():
            if user.username == username and user.hashed_password == self._hash_password(password):
                user.last_login = datetime.now()
                return user
        return None
    
    def create_user(self, username: str, email: str, password: str, roles: list[str] = None) -> typing.Optional[User]:
        """
        Create a new user with specified details.
        
        :param username: Desired username
        :param email: User's email address
        :param password: User's password
        :param roles: Optional list of user roles
        :return: Created user or None if username/email exists
        """
        user = User(
            username=username,
            email=email,
            hashed_password=self._hash_password(password),
            roles=roles or ['analyst']
        )
        
        return user if self.add_user(user) else None
    
    def update_user_roles(self, user_id: str, new_roles: list[str]) -> bool:
        """
        Update roles for a specific user.
        
        :param user_id: User's unique ID
        :param new_roles: List of new roles
        :return: True if update successful, False otherwise
        """
        if user_id not in self._users:
            return False
        
        # Validate roles
        if not all(role in self._roles for role in new_roles):
            return False
        
        self._users[user_id].roles = new_roles
        return True
    
    def check_permission(self, user: User, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        :param user: User to check permissions for
        :param permission: Permission to verify
        :return: True if user has permission, False otherwise
        """
        return any(
            permission in self._roles.get(role, [])
            for role in user.roles
        )
    
    def get_user(self, user_id: str) -> typing.Optional[User]:
        """
        Retrieve a user by their ID.
        
        :param user_id: User's unique ID
        :return: User object or None
        """
        return self._users.get(user_id)
    
    def list_users(self) -> list[User]:
        """
        List all users in the system.
        
        :return: List of all users
        """
        return list(self._users.values())

def main():
    """Example usage of UserManager."""
    user_manager = UserManager()
    
    # Create users
    admin = user_manager.create_user('admin', 'admin@example.com', 'admin_pass', ['admin'])
    analyst = user_manager.create_user('analyst', 'analyst@example.com', 'analyst_pass', ['analyst'])
    
    # Authenticate users
    authenticated_admin = user_manager.authenticate('admin', 'admin_pass')
    
    # Check permissions
    if authenticated_admin:
        print(f"Admin can view security logs: {user_manager.check_permission(authenticated_admin, 'view_security_logs')}")

if __name__ == '__main__':
    main()
