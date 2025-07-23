from flask import Blueprint, jsonify, request

from .models import db, URLMap
from .views import get_unique_short_id

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')


@api_bp.route('/id/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify(message='"url" является обязательным полем!'), 400

    original = data.get('url')
    custom_id = (data.get('custom_id') or '').strip()

    if custom_id:
        if not custom_id.isalnum() or len(custom_id) > 16:
            return jsonify(
                message='Указано недопустимое имя для короткой ссылки'), 400

        if custom_id.lower() == 'files':
            return jsonify(
                message='Предложенный вариант короткой ссылки уже существует.'
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


@api_bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify(message='Указанный id не найден'), 404

    return jsonify(url=url_map.original), 200
