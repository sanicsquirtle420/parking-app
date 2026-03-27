import mariadb
import os
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

load_dotenv()

SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT"))
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_connection():
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT),
        local_bind_address=('127.0.0.1', 0)  # auto port
    )

    tunnel.start()
    print(f"SSH tunnel established on local port {tunnel.local_bind_port}")

    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        database=DB_NAME
    )

    return conn
