from http import HTTPStatus

from flask import jsonify, request

from . import app
from .models import URLMap
from .exceptions import URLMapException


@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json(silent=True)
    if not data:
        raise URLMapException(
            app.config['MISSING_REQUEST_BODY'],
            HTTPStatus.BAD_REQUEST
        )
    if 'original_url' not in data:
        raise URLMapException(
            app.config['URL_FIELD_REQUIRED'],
            HTTPStatus.BAD_REQUEST
        )
    original_url = data.get('original_url')
    custom_short = data.get('custom_short', '').strip()
    try:
        url_map = URLMap.create_url_map(original_url, custom_short or None)
        return jsonify(
            original_url=url_map.original_url,
            short=url_map.get_short_url()
        ), HTTPStatus.CREATED
    except URLMapException as e:
        raise e


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    url_map = URLMap.get_by_short(short)
    if not url_map:
        raise URLMapException(app.config['ID_NOT_FOUND'], HTTPStatus.NOT_FOUND)
    return jsonify(original_url=url_map.original_url), HTTPStatus.OK
