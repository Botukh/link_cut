from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config
from .exceptions import ValidationError, APIError

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.errorhandler(ValidationError)
def handle_url_map_exception(error):
    return jsonify({'message': error.message}), error.status_code


@app.errorhandler(APIError)
def handle_api_error(error):
    return jsonify(message=error.message), error.status_code


from . import api_views, error_handlers, forms, views, ydisk, forms, exceptions
