"""
api/db.py
=========
MySQL connection for the FastAPI layer.
Points at the Docker container on port 3307.
"""

import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "parking123",
    "database": "parking_db",
}


def get_connection():
    """Return a live MySQL connection. Caller is responsible for closing."""
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    """Quick sanity check — run `python db.py` to verify."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()[0]
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Connected to {db}")
        print(f"Tables: {tables}")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    test_connection()
