from http import HTTPStatus

from flask import jsonify, render_template

from . import app, db
from .exceptions import APIError


@app.errorhandler(APIError)
def handle_api_error(error):
    return jsonify(message=error.message), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
