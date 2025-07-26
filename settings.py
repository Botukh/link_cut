import os
import string
import re

SHORT_LENGTH = 16
CHARS = string.ascii_letters + string.digits
SHORT_CHARS_PATTERN = rf'^[{re.escape(CHARS)}]+$'
MAX_SHORT_GENERATION_ATTEMPTS = 100
SHORT_DEFAULT_LENGTH = 6
REDIRECT_VIEW_ENDPOINT = 'redirect_view'


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
