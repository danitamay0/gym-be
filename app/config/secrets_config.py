import os


BE_ENV = os.getenv("SMART_STORE_ENV")
SECRET_PROJECT_ID = os.getenv("SECRET_PROJECT_ID")  # to g
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.dirname(__file__)
print(BE_ENV)

if BE_ENV == "dev":
    from dotenv import load_dotenv

    load_dotenv()
    POSTGRES_LOCAL_BASE = os.getenv("SMART_STORE_DB_SERVER_URL")
    DATABASE_NAME = os.getenv("SMART_STORE_DB_NAME")
    BASE_DOMAIN = os.getenv("SMART_STORE_DB_NAME")
    DISABLE_SWAGGER = os.getenv("DISABLE_SWAGGER")
    # SMART_SECURE_FILE_PATH = os.getenv("SMART_SECURE_FILE_PATH")
    # app.py
    SECRET_KEY = os.getenv("SECRET_KEY")
    print(POSTGRES_LOCAL_BASE, DATABASE_NAME)

else:
    # from configurations.load_secrets_config import secrets
    secrets = []
    """ BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    POSTGRES_LOCAL_BASE = secrets["MY_ACCOUNT_DB_SERVER_URL"]
    DATABASE_NAME = secrets["MY_ACCOUNT_DB_NAME"]
    BASE_DOMAIN = secrets["MY_ACCUNT_DOMAIN_URL"]
   
    DISABLE_SWAGGER = secrets["DISABLE_SWAGGER"] """

    # SMART_SECURE_FILE_PATH = os.getenv("SMART_SECURE_FILE_PATH")
