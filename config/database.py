import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def connect(self):
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )

db = Database()
