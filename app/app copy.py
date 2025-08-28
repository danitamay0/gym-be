# server/app.py
from pathlib import Path
from config.secrets_config import DATABASE_NAME, POSTGRES_LOCAL_BASE
from database import db, migrate
from flask import Flask, send_from_directory
from flask_cors import CORS
from api.register_all_routes import *  # noqa
from rebar import rebar

ROOT = Path(__file__).resolve().parent.parent  # ajusta si tu layout es distinto
FRONT_DIST = ROOT / "frontend" / "dist"        # ruta al build de Vite

def create_app():
    app = Flask(
        __name__,
        static_folder=str(FRONT_DIST),
        static_url_path="/",
    )

    # Rebar/OpenAPI
    rebar.init_app(app)

    # DB
    app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_LOCAL_BASE + DATABASE_NAME
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app)

    # CORS solo para API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Rutas SPA: sirve archivos del build y fallback a index.html
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        target = FRONT_DIST / path
        if target.is_file():
            # sirve /assets/* y demás archivos generados por Vite
            return send_from_directory(FRONT_DIST, path)
        # fallback SPA
        return send_from_directory(FRONT_DIST, "index.html")

    return app

# ⚠️ Gunicorn usará este callable
app = create_app()

if __name__ == "__main__":
    # Útil para pruebas locales
    app.run(debug=True, host="0.0.0.0", port=8000)
