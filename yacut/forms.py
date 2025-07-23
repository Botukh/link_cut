from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(), URL(message="Некорректный URL")]
    )
    custom_id = StringField(
        'Короткая ссылка (по желанию)',
        validators=[Optional(), Length(max=16),
                    Regexp(r'^[a-zA-Z0-9]+$', message="Только буквы и цифры")]
    )


class FileUploadForm(FlaskForm):

    files = MultipleFileField(
        'Выберите файлы',
        validators=[
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf',
                 'doc', 'docx', 'txt', 'zip'],
                message='Недопустимый тип файла'
            )
        ]
    )
