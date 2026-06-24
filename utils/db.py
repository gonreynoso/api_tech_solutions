import psycopg2
import psycopg2.extras

from config import Config


def get_connection():
    return psycopg2.connect(Config.db_dsn())


def query(sql, params=None, fetch="all"):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            if fetch == "none":
                conn.commit()
                return None
            result = cur.fetchall() if fetch == "all" else cur.fetchone()
            conn.commit()
            return result
    finally:
        conn.close()
