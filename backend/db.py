# backend/db.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cursor = conn.cursor()
