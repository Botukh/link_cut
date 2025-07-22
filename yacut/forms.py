from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp


class URLForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(), URL(message="Некорректный URL")]
    )
    custom_id = StringField(
        'Короткая ссылка (по желанию)',
        validators=[Optional(), Length(max=16),
                    Regexp(r'^[a-zA-Z0-9]+$', message="Только буквы и цифры")]
    )
