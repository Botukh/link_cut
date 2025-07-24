from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField
from wtforms.validators import DataRequired, Length, Regexp, URL, Optional

from . import app


class URLMapForm(FlaskForm):
    original_link = StringField(
        app.config['LONG_LINK_LABEL'],
        validators=[
            DataRequired(message=app.config['URL_FIELD_REQUIRED']),
            URL(message=app.config['INCORRECT_URL'])
        ]
    )
    custom_id = StringField(
        app.config['SHORT_LINK_LABEL'],
        validators=[
            Optional(),
            Length(max=app.config['SHORT_LENGTH']),
            Regexp(
                app.config['SHORT_CHARS_PATTERN'],
                message=app.config['ONLY_LETTERS_NUMBERS']
            )
        ]
    )


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        app.config['CHOOSE_FILES'],
        validators=[DataRequired(message=app.config['NO_FILES_TO_UPLOAD'])]
    )
