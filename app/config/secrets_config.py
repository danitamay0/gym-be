import os
from pathlib import Path
from dotenv import load_dotenv

BE_ENV = os.getenv("SMART_STORE_ENV", "")  # "docker", "dev", "prod", etc.

# Solo carga .env si existe Y NO estás en docker/prod.
# Además, no sobrescribas lo que venga del entorno (override=False).
if BE_ENV not in {"docker", "prod"} and Path(".env").exists():
    load_dotenv(override=False)

POSTGRES_LOCAL_BASE = os.getenv("SMART_STORE_DB_SERVER_URL")
DATABASE_NAME = os.getenv("SMART_STORE_DB_NAME")

# Evita este bug: estabas copiando el nombre de la DB al dominio
BASE_DOMAIN = os.getenv("BASE_DOMAIN", "localhost")

DISABLE_SWAGGER = os.getenv("DISABLE_SWAGGER")
SECRET_KEY = os.getenv("SECRET_KEY")
