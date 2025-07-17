from config.secrets_config import DATABASE_NAME
from config.secrets_config import POSTGRES_LOCAL_BASE
from database import db
from database import migrate
from flask import Flask
from flask_cors import CORS
from api.register_all_routes import *  # noqa # pylint: disable=unused-import
from rebar import rebar


def create_app():
    app = Flask(__name__)
    rebar.init_app(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_LOCAL_BASE + DATABASE_NAME
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    return app


if __name__ == "__main__":
    app = create_app().run(debug=True, host="0.0.0.0")
