from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, MultipleFileField
from wtforms.validators import DataRequired, Length, Regexp, URL, Optional

from settings import SHORT_LENGTH, SHORT_CHARS_PATTERN


LONG_LINK_LABEL = 'Длинная ссылка'
URL_FIELD_REQUIRED = '"url" является обязательным полем!'
INCORRECT_URL = 'Некорректный URL'
SHORT_LINK_LABEL = 'Короткая ссылка (по желанию)'
ONLY_LETTERS_NUMBERS = 'Только буквы и цифры'
CHOOSE_FILES = 'Выберите файлы'
NO_FILES_TO_UPLOAD = 'Нет файлов для загрузки'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx']
INVALID_FILE_TYPE = 'Недопустимый тип файла'


class URLMapForm(FlaskForm):
    original_link = StringField(
        LONG_LINK_LABEL,
        validators=[DataRequired(message=URL_FIELD_REQUIRED),
                    URL(message=INCORRECT_URL)
                    ]
    )
    custom_id = StringField(
        SHORT_LINK_LABEL,
        validators=[
            Optional(),
            Length(max=SHORT_LENGTH),
            Regexp(SHORT_CHARS_PATTERN,
                   message=ONLY_LETTERS_NUMBERS)
        ]
    )


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        CHOOSE_FILES,
        validators=[
            DataRequired(message=NO_FILES_TO_UPLOAD),
            FileAllowed(ALLOWED_EXTENSIONS, message=INVALID_FILE_TYPE)
        ]
    )
