import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get Supabase database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found in .env file")

# Connect to Supabase PostgreSQL
connection = psycopg2.connect(DATABASE_URL)

print("Supabase PostgreSQL connected successfully!")

# Check database connection
cursor = connection.cursor()

cursor.execute("""
    SELECT current_database(), current_user, inet_server_addr(), inet_server_port();
""")

print("DATABASE TEST:", cursor.fetchone())

cursor.close()