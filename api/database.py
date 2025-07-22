import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from api.config import settings

class DatabaseConnection:
    @staticmethod
    @contextmanager
    def get_connection():
        connection = None
        try:
            connection = mysql.connector.connect(
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection and connection.is_connected():
                connection.close()

# SQL Injection Protection
def sanitize_table_name(exam: str, tour: str) -> str:
    """Sanitize table name to prevent SQL injection"""
    allowed_exams = ['CEP', 'BEPC', 'BAC']
    allowed_tours = ['1er', '2nd']
    
    if exam.upper() not in allowed_exams:
        raise ValueError("Invalid exam type")
    if tour not in allowed_tours:
        raise ValueError("Invalid tour")
    
    return f"resultats_{exam.upper()}_{tour.replace('er', 'er').replace('nd', 'nd')}"

def sanitize_input(input_string: str) -> str:
    """Basic input sanitization"""
    if not isinstance(input_string, str):
        raise ValueError("Input must be string")
    
    # Remove dangerous characters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()