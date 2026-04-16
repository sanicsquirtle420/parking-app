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

_tunnel_lock = threading.Lock()
_pool_lock = threading.Lock()
_tunnel = None
pool = None

def _init_pool():
    global _tunnel, pool
    with _pool_lock:
        if pool is not None:
            return
        
        if _tunnel is None or not _tunnel.is_active:
            _tunnel = _get_tunnel()
        try:
            pool = mariadb.ConnectionPool(
                    host="127.0.0.1",
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    port=_tunnel.local_bind_port,
                    pool_name = "387_pool",
                    pool_size = 5,
                    connect_timeout=5,
                    autocommit=False
                )
        except mariadb.PoolError:
            pool = mariadb.ConnectionPool(pool_name="387_pool")
            
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
    t = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT),
        local_bind_address=("127.0.0.1", 0),
    )
    t.daemon_forward_servers = True
    t.start()
    print(f"SSH tunnel established on local port {t.local_bind_port}")
    return t


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
    global pool
    if pool is None:
        _init_pool()
    return ManagedConnection(pool.get_connection())

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