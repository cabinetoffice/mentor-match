import configparser
import os
import secrets

from flask import Flask

from .config import Config
from .tasks import make_celery


def create_app(configuration=Config):
    app = Flask(__name__, static_folder="static")

    app.config.from_object(configuration)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "data")
    parser = configparser.ConfigParser()
    parser.read("./.bumpversion.cfg")
    app.config["VERSION"] = parser["bumpversion"]["current_version"]

    from app.main import main_bp
    from app.auth import auth_bp
    from app.notify import notify_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(notify_bp)

    app.secret_key = secrets.token_urlsafe(48)

    make_celery(app)

    return app
