from http import HTTPStatus

from flask import jsonify, render_template, request

from . import app, db
from .exceptions import APIError
from .models import URLMapValidationError


@app.errorhandler(URLMapValidationError)
def handle_validation_error(error):
    if request.path.startswith('/api/'):
        return jsonify(message=error.message), HTTPStatus.BAD_REQUEST
    else:
        return render_template(
            'errors/400.html',
            message=error.message
        ), HTTPStatus.BAD_REQUEST


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
