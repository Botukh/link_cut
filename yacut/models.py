import string
import random
from datetime import datetime, timezone

from flask import url_for

from . import db
from . import app
from .exceptions import URLMapException


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short = db.Column(
        db.String(
            app.config['SHORT_LENGTH']
        ),
        unique=True,
        index=True,
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    CHARS = string.ascii_letters + string.digits

    @staticmethod
    def create_url_map(original_url, custom_short=None):
        if custom_short:
            custom_short = custom_short.strip()
            if not URLMap._validate_short(custom_short):
                raise URLMapException(app.config['INVALID_SHORT_NAME'])
            if URLMap._short_exists(custom_short):
                raise URLMapException(app.config['SHORT_LINK_EXISTS'])
            short = custom_short
        else:
            short = URLMap._generate_unique_short()
        url_map = URLMap(original_url=original_url, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_by_short(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def _validate_short(short):
        import re
        return (re.match(app.config['SHORT_CHARS_PATTERN'], short) and
                len(short) <= app.config['SHORT_LENGTH'] and
                short.lower() != 'files')

    @staticmethod
    def _short_exists(short):
        return URLMap.query.filter_by(short=short).first() is not None

    @staticmethod
    def _generate_unique_short(length=None):
        if length is None:
            length = app.config['SHORT_ID_DEFAULT_LENGTH']
        for _ in range(app.config['MAX_RETRY_ATTEMPTS']):
            short = ''.join(random.choices(URLMap.CHARS, k=length))
            if not URLMap._short_exists(short):
                return short
        raise URLMapException(
            'Не удалось сгенерировать уникальную короткую ссылку'
        )

    def get_short_url(self):
        return url_for('redirect_view', short=self.short, _external=True)

    @staticmethod
    def batch_create(file_data_list):
        created_records = []
        for filename, public_url in file_data_list:
            if public_url:
                short = URLMap._generate_unique_short()
                url_map = URLMap(original_url=public_url, short=short)
                db.session.add(url_map)
                created_records.append({
                    'filename': filename,
                    'short': short,
                    'public_url': public_url
                })
        db.session.commit()
        return created_records
