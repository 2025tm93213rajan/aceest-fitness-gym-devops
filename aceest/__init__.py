import os

from flask import Flask

from aceest import db
from aceest.routes import bp

DEFAULT_VERSION = "2.0.0"
DEFAULT_RELEASE = "v2-stable"


def create_app(config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("ACEEST_DB", "aceest_fitness.db")
    app.config["VERSION"] = os.environ.get("APP_VERSION", DEFAULT_VERSION)
    app.config["RELEASE"] = os.environ.get("APP_RELEASE", DEFAULT_RELEASE)

    # tests pass their own config (temp db path etc.)
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)
    return app
