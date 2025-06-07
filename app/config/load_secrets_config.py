import json
import os

from google.cloud import secretmanager

secrets_env = os.getenv("SECRETS_ENV")
secrets_env_version = os.getenv("SECRETS_ENV_V")
secret_project_id = os.getenv("SECRET_PROJECT_ID")
be_env = os.getenv("BE_ENV")

if secrets_env and secrets_env_version and be_env != "dev":
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(secret_project_id, secrets_env, "latest")
    secrets_path = f"projects/{secret_project_id}/secrets/{secrets_env}/versions/{secrets_env_version}"
    response = client.access_secret_version(request={"name": secrets_path})
    secrets = json.loads(response.payload.data)
else:
    secrets = {
        "SECURITY_PASSWORD_SALT": "",
        "SMART_STORE_DOMAIN_URL": "",
        "SMART_STORE_DB_SERVER_URL": "",
        "SMART_STORE_DB_NAME": "",
        "DISABLE_SWAGGER": False,
    }
