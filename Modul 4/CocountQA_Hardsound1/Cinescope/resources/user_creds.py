import os
from dotenv import load_dotenv

load_dotenv()  # загрузит переменные из .env

class SuperAdminCreds:
    USERNAME = os.getenv("SUPER_ADMIN_USERNAME")
    PASSWORD = os.getenv("SUPER_ADMIN_PASSWORD")