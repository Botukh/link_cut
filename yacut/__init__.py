from flask import Flask, Blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
main_bp = Blueprint('main', __name__)

from . import api_views, error_handlers, forms, views, utils, ydisk, forms

app.register_blueprint(main_bp)