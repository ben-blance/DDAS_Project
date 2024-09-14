import psycopg2
from psycopg2 import sql

# Database connection parameters
DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"  # Update with your database URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_hashes (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            sha256_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def insert_hash(filename: str, sha256_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO file_hashes (filename, sha256_hash) VALUES (%s, %s)", (filename, sha256_hash))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_hashes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, sha256_hash FROM file_hashes")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
