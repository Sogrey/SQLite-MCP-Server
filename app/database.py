import sqlite3
from typing import Tuple
from sqlite3 import Connection, Cursor
from config import Config

def get_conn() -> Tuple[Connection, Cursor]:
    """获取数据库连接和游标
    
    Returns:
        Tuple[Connection, Cursor]: (数据库连接, 游标)
    """
    conn = sqlite3.connect(Config.SQLITE_DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()