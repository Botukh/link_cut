import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
    SHORT_LENGTH = 16
    SHORT_CHARS_PATTERN = r'^[a-zA-Z0-9]+$'
    MAX_RETRY_ATTEMPTS = 100
    SHORT_ID_DEFAULT_LENGTH = 6
    MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
    URL_FIELD_REQUIRED = '"url" является обязательным полем!'
    INVALID_SHORT_NAME = 'Указано недопустимое имя для короткой ссылки'
    SHORT_LINK_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
    ID_NOT_FOUND = 'Указанный id не найден'
    INCORRECT_URL = 'Некорректный URL'
    CHOOSE_FILES = 'Выберите файлы'
    INVALID_FILE_TYPE = 'Недопустимый тип файла'
    NO_FILES_TO_UPLOAD = 'Нет файлов для загрузки'
    FILE_UPLOAD_ERROR = 'Ошибка загрузки файлов'
    LONG_LINK_LABEL = 'Длинная ссылка'
    SHORT_LINK_LABEL = 'Короткая ссылка (по желанию)'
    ONLY_LETTERS_NUMBERS = 'Только буквы и цифры'
