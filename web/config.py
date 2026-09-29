import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:5000")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")