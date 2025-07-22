from flask import Blueprint, request, jsonify

from .models import URLMap
from . import db
from .utils import get_unique_short_id

api_bp = Blueprint('api', __name__)


@api_bp.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json()
    if not data:
        return jsonify(message='Отсутствует тело запроса'), 400

    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        return jsonify(message='"url" является обязательным полем!'), 400

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

    new_link = URLMap(original=url, short=short)
    db.session.add(new_link)
    db.session.commit()

    return jsonify(url=url, short_link=request.host_url + short), 201


@api_bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify(message='Указанный id не найден'), 404
    return jsonify(url=url_map.original), 200
