from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp

from . import app


class URLMapForm(FlaskForm):
    original = StringField(
        app.config['LONG_LINK_LABEL'],
        validators=[DataRequired(), URL(message=app.config['INCORRECT_URL'])]
    )
    custom_short = StringField(
        app.config['SHORT_LINK_LABEL'],
        validators=[Optional(), Length(max=app.config['SHORT_LENGTH']),
                    Regexp(
                        app.config['SHORT_CHARS_PATTERN'],
                        message=app.config['ONLY_LETTERS_NUMBERS']
        )]
    )


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        app.config['CHOOSE_FILES'],
        validators=[
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf',
                 'doc', 'docx', 'txt', 'zip'],
                message=app.config['INVALID_FILE_TYPE']
            )
        ]
    )
