from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, URL, Optional

from settings import SHORT_LENGTH, SHORT_CHARS_PATTERN

LONG_LINK_LABEL = 'Длинная ссылка'
URL_FIELD_REQUIRED = '"url" является обязательным полем!'
INCORRECT_URL = 'Некорректный URL'
URL_TOO_LONG = 'URL слишком длинный (максимум 2048 символов)'
SHORT_LINK_LABEL = 'Короткая ссылка (по желанию)'
ONLY_LETTERS_NUMBERS = 'Только буквы и цифры'
CHOOSE_FILES = 'Выберите файлы'
NO_FILES_TO_UPLOAD = 'Нет файлов для загрузки'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx']
INVALID_FILE_TYPE = f'Недопустимый тип файла. Разрешены: {", ".join(
    ALLOWED_EXTENSIONS
)}'
SUBMIT_BUTTON = 'Создать'
UPLOAD_BUTTON = 'Загрузить'


class URLMapForm(FlaskForm):
    original_link = StringField(
        LONG_LINK_LABEL,
        validators=[
            DataRequired(message=URL_FIELD_REQUIRED),
            URL(message=INCORRECT_URL),
            Length(max=2048, message=URL_TOO_LONG)
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
    submit = SubmitField(SUBMIT_BUTTON)


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        CHOOSE_FILES,
        validators=[
            DataRequired(message=NO_FILES_TO_UPLOAD),
            FileAllowed(ALLOWED_EXTENSIONS, message=INVALID_FILE_TYPE)
        ]
    )
    submit = SubmitField(UPLOAD_BUTTON)
