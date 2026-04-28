from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
import mariadb
import os
import threading
from kivy.clock import Clock

load_dotenv()

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

_key_locks = {}
_key_locks_lock = threading.Lock()


class ManagedConnection:
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
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT),
        local_bind_address=("127.0.0.1", 0),
        allow_agent=False,
        host_pkey_directories=[],
        set_keepalive=10.0,
        mute_exceptions=True,
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
    tunnel = _get_tunnel()
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host="127.0.0.1",
        port=tunnel.local_bind_port,
        database=DB_NAME,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )
    return ManagedConnection(conn)


def run_in_background(fetch_fn, callback_fn, task_key=None):
    if task_key is not None:
        with _key_locks_lock:
            if task_key not in _key_locks:
                _key_locks[task_key] = threading.Lock()
            lock = _key_locks[task_key]

        if not lock.acquire(blocking=False):
            print(f"DEBUG: '{task_key}' already in progress, skipping duplicate.")
            return
    else:
        lock = None

    def _worker():
        try:
            result = fetch_fn()
        except Exception as e:
            print(f"Background task error ({task_key or 'unnamed'}):", e)
            result = None
        finally:
            if lock is not None:
                lock.release()

        if callback_fn:
            Clock.schedule_once(lambda dt: callback_fn(result), 0)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

def warmup():
    try:
        _get_tunnel()
        print("DEBUG: tunnel warmed up")
    except Exception as e:
        print("Tunnel warmup failed:", e)