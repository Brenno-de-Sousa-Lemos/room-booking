import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRA_MIN = 60

TERMO_VERSAO = "1.0"
POLITICA_VERSAO = "1.0"