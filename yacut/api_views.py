from flask import jsonify, request
import re
from .models import db, URLMap
from .views import get_unique_short_id
from . import app


@app.route('/api/id/', methods=['POST'])
def create_short_url():

    if not request.get_json(silent=True):
        return jsonify(message='Отсутствует тело запроса'), 400

    data = request.get_json()

    if 'url' not in data:
        return jsonify(message='"url" является обязательным полем!'), 400

    original = data.get('url')
    custom_id = data.get('custom_id', '').strip()

    if custom_id:
        if not re.match(r'^[a-zA-Z0-9]+$', custom_id) or len(custom_id) > 16:
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
        short_link=request.host_url.rstrip('/') + '/' + url_map.short
    ), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify(message='Указанный id не найден'), 404

    return jsonify(url=url_map.original), 200
