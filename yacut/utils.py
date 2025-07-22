import random
import string
import asyncio

from .models import URLMap

CHARS = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 6


def get_unique_short_id(length=SHORT_ID_LENGTH):
    while True:
        short_id = ''.join(random.choices(CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def run_async(func, *args, **kwargs):
    return asyncio.run(func(*args, **kwargs))
