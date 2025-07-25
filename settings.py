import os

SHORT_LENGTH = 16
SHORT_CHARS_PATTERN = r'^[a-zA-Z0-9]+$'
MAX_RETRY_ATTEMPTS = 100
SHORT_ID_DEFAULT_LENGTH = 6


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
