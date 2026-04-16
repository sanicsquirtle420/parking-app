"""
db_connection.py
================
MySQL database connection handler for the Ole Miss Campus Parking App.

This file manages the connection to the MySQL database running in Docker.
Every other Python file imports `get_connection()` from here.

SETUP:
  - MySQL runs in Docker on port 3307 (mapped from container's 3306)
  - Database: parking_db
  - To start the database:
    docker run --name olemiss-parking -e MYSQL_ROOT_PASSWORD=parking123 \
               -e MYSQL_DATABASE=parking_db -p 3307:3306 -d mysql:8.0

INSTALL REQUIRED PACKAGE:
  pip install mysql-connector-python

USAGE IN OTHER FILES:
  from db_connection import get_connection

  conn = get_connection()
  cursor = conn.cursor(dictionary=True)
  cursor.execute("SELECT * FROM parking_lots")
  results = cursor.fetchall()
  cursor.close()
  conn.close()
"""

import mysql.connector
from mysql.connector import Error


# Database configuration — update these if your Docker setup is different
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "parking123",
    "database": "parking_db"
}


def get_connection():
    """
    Returns a MySQL connection object.
    Call this at the start of any database operation.
    Always close the connection when done.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def test_connection():
    """
    Quick test to verify the database is reachable.
    Run this file directly to test: python db_connection.py
    """
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")

        cursor.close()
        conn.close()
    else:
        print("Failed to connect. Is Docker running?")
        print("Start it with: docker start olemiss-parking")


if __name__ == "__main__":
    test_connection()
