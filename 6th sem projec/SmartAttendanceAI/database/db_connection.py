"""SmartAttendanceAI – MySQL Connection Pool"""
import logging
import mysql.connector
from mysql.connector import pooling
from backend.config import Config

logger = logging.getLogger(__name__)
_pool  = None

def _get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="smart_pool", pool_size=10,
            host=Config.MYSQL_HOST, port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER, password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB, autocommit=False,
        )
        logger.info("MySQL pool initialised.")
    return _pool

def get_db_connection():
    try:
        return _get_pool().get_connection()
    except Exception as e:
        logger.critical("DB connection failed: %s", e); raise