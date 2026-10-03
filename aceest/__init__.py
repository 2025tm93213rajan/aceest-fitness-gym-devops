import os

from flask import Flask

from aceest import db
from aceest.routes import bp


def create_app(config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("ACEEST_DB", "aceest_fitness.db")

    # tests pass their own config (temp db path etc.)
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)
    return app
