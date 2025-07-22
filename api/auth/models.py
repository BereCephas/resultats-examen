from api.database import DatabaseConnection
from api.core.security import get_password_hash, verify_password
from typing import Optional, Dict, Any

class UserModel:
    @staticmethod
    def create_user(user_data: dict) -> bool:
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Hash password
            hashed_password = get_password_hash(user_data['password'])
            
            query = """
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                user_data['username'],
                user_data['email'],
                hashed_password,
                user_data['role'],
                True
            ))
            conn.commit()
            return True
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[Any, Any]]:
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM users WHERE username = %s AND is_active = true"
            cursor.execute(query, (username,))
            return cursor.fetchone()
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[Any, Any]]:
        user = UserModel.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user['password_hash']):
            return None
        return user
    
    @staticmethod
    def get_all_users() -> list:
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT id, username, email, role, is_active, created_at 
            FROM users ORDER BY created_at DESC
            """
            cursor.execute(query)
            return cursor.fetchall()