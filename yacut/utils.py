import random
import string

from .models import URLMap

CHARS = string.ascii_letters + string.digits


def get_unique_short_id():
    length = random.randint(4, 16)
    while True:
        short_id = ''.join(random.choices(CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
