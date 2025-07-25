from http import HTTPStatus

from flask import jsonify, request

from . import app
from .exceptions import APIError
from .models import URLMap, URLMapValidationError


MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
URL_FIELD_REQUIRED = '"url" является обязательным полем!'
ID_NOT_FOUND = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json(silent=True)
    if not data:
        raise APIError(MISSING_REQUEST_BODY, HTTPStatus.BAD_REQUEST)
    if 'url' not in data:
        raise APIError(URL_FIELD_REQUIRED, HTTPStatus.BAD_REQUEST)

    original = data['url']
    custom_id = data.get('custom_id')

    try:
        return jsonify(
            url=original,
            short_link=URLMap.create(original, custom_id).get_short_url()
        ), HTTPStatus.CREATED
    except URLMapValidationError as e:
        raise APIError(str(e))


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    url_map = URLMap.get(short)
    if not url_map:
        raise APIError(ID_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify(url=url_map.original), HTTPStatus.OK
