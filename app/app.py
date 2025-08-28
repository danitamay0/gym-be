from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config.secrets_config import DATABASE_NAME, POSTGRES_LOCAL_BASE
from database import db, migrate
from api.register_all_routes import *  # noqa
from rebar import rebar

FRONT_DIST = Path(__file__).parent / "fronted" / "dist"  # <- tu build

def create_app():
    app = Flask(
        __name__,
        static_folder=str(FRONT_DIST),
        static_url_path="",   # <- IMPORTANTE: vacío, no "/"
    )

    rebar.init_app(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_LOCAL_BASE + DATABASE_NAME
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ---- Debug rápido
    print("FRONT_DIST ->", FRONT_DIST.resolve())
    print("INDEX EXISTS? ->", (FRONT_DIST / "index.html").exists())

    @app.get("/__ping")
    def ping():
        return "pong"

    # Sirve SPA (fallback a index.html)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        target = FRONT_DIST / path
        if target.is_file():
            return send_from_directory(str(FRONT_DIST), path)
        return send_from_directory(str(FRONT_DIST), "index.html")

    return app
print("aaaaa")
app = create_app()
