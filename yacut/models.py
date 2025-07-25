import string
import random
import re
from datetime import datetime, timezone

from flask import url_for

from . import db
from .exceptions import ValidationError
from settings import (
    SHORT_LENGTH,
    SHORT_CHARS_PATTERN,
    MAX_RETRY_ATTEMPTS,
    SHORT_ID_DEFAULT_LENGTH
)


ORIGINAL_URL_MAX_LENGTH = 2048
CHARS = string.ascii_letters + string.digits
GENERATION_ERROR_MESSAGE = (
    'Не удалось сгенерировать уникальную короткую ссылку'
    f'за {MAX_RETRY_ATTEMPTS} попыток'
)
INVALID_ORIGINAL_NAME = 'URL слишком длинный'
INVALID_SHORT_NAME = 'Указано недопустимое имя для короткой ссылки'
SHORT_LINK_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_URL_MAX_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_LENGTH),
        unique=True,
        index=True,
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def create(original, custom_short=None):
        if len(original) > ORIGINAL_URL_MAX_LENGTH:
            raise ValidationError(INVALID_ORIGINAL_NAME)

        if custom_short:
            if len(custom_short) > SHORT_LENGTH:
                raise ValidationError(INVALID_SHORT_NAME)
            if not re.match(SHORT_CHARS_PATTERN, custom_short):
                raise ValidationError(INVALID_SHORT_NAME)
            if URLMap.get(custom_short):
                raise ValidationError(SHORT_LINK_EXISTS)
            short = custom_short
        else:
            short = URLMap._generate_unique_short()
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def _generate_unique_short():
        for _ in range(MAX_RETRY_ATTEMPTS):
            short = ''.join(random.choices(CHARS, k=SHORT_ID_DEFAULT_LENGTH))
            if not URLMap.get(short) and short != 'files':
                return short
        raise ValidationError(GENERATION_ERROR_MESSAGE)

    def get_short_url(self):
        return url_for('redirect_view', short=self.short, _external=True)

    @staticmethod
    def batch_create(file_data_list):
        return [
            {
                'filename': filename,
                'short_url': URLMap.create(url).get_short_url()
            }
            for filename, url in file_data_list if url
        ]
