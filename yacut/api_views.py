from flask import Blueprint, jsonify, request
from . import db
from .models import URLMap
from .utils import get_unique_short_id

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_url():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify(message='\"url\" is a required field!'), 400

    original = data.get('url')
    custom_id = data.get('custom_id')
    custom_id = custom_id.strip() if custom_id else ''

    if custom_id:
        if not custom_id.isalnum() or len(custom_id) > 16:
            return jsonify(
                message='Указано недопустимое имя для короткой ссылки'
            ), 400
        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify(
                message='Предложенный вариант короткой ссылки уже существует.'
            ), 400
        short = custom_id
    else:
        short = get_unique_short_id()

    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()

    return jsonify(
        url=url_map.original,
        short_link=request.host_url + url_map.short
    ), 201
