from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import api_views, error_handlers, forms, views, utils, ydisk, forms
from .views import main_bp


app.register_blueprint(main_bp)