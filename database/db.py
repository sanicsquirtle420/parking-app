from pathlib import Path
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
import mysql.connector as mariadb
import os
import threading
from kivy.clock import Clock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOTENV_PATHS = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "database" / ".env",
]

for dotenv_path in DOTENV_PATHS:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)

SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

_tunnel = None
_tunnel_lock = threading.Lock()


def _format_env_locations():
    return ", ".join(str(path) for path in DOTENV_PATHS)


def _validate_db_config():
    missing = [name for name, value in {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_NAME": DB_NAME,
    }.items() if not value]

    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(
            "Missing required database settings: "
            f"{missing_text}. Create a .env file in one of: {_format_env_locations()}."
        )


def _validate_tunnel_config():
    missing = [name for name, value in {
        "SSH_HOST": SSH_HOST,
        "SSH_USER": SSH_USER,
        "SSH_PASSWORD": SSH_PASSWORD,
    }.items() if not value]

    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(
            "SSH tunneling is enabled but required settings are missing: "
            f"{missing_text}. Update your .env file in one of: {_format_env_locations()}."
        )


class ManagedConnection:
    """Wrapper so existing code can keep calling conn.close()."""
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, item):
        return getattr(self._conn, item)

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


def _start_tunnel():
    _validate_tunnel_config()

    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT),
        local_bind_address=("127.0.0.1", 0),
    )
    tunnel.daemon_forward_servers = True
    tunnel.start()
    print(f"SSH tunnel established on local port {tunnel.local_bind_port}")
    return tunnel


def _get_tunnel():
    global _tunnel
    with _tunnel_lock:
        if _tunnel is not None and _tunnel.is_active:
            return _tunnel

        if _tunnel is not None:
            try:
                _tunnel.stop()
            except Exception:
                pass

        _tunnel = _start_tunnel()
        return _tunnel


def get_connection():
    _validate_db_config()
    tunnel = _get_tunnel()
    host = "127.0.0.1"
    port = tunnel.local_bind_port

    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=host,
            port=port,
            database=DB_NAME,
            connect_timeout=5,
            autocommit=False,
        )
    except mariadb.Error as exc:
        if getattr(exc, "errno", None) == 1045:
            raise RuntimeError(
                f"Database login failed for user '{DB_USER}' at {host}:{port}. "
                f"Check DB_USER, DB_PASSWORD, and DB_NAME in your .env file. "
                f"Searched: {_format_env_locations()}."
            ) from exc
        raise

    return ManagedConnection(conn)


def run_in_background(fetch_fn, callback_fn):
    """Run fetch_fn in a daemon thread; deliver result to callback_fn on Kivy main thread."""
    def _worker():
        try:
            result = fetch_fn()
        except Exception as e:
            print("Background task error:", e)
            result = None

        if callback_fn:
            Clock.schedule_once(lambda dt: callback_fn(result), 0)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
