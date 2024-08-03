import textwrap
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models


def make_shorter( filtering_str, filtering_width=100):
    return textwrap.shorten(filtering_str, width=filtering_width, placeholder="...")


app.jinja_env.filters['make_shorter'] = make_shorter