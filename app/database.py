import sqlite3
from typing import Tuple, Optional, Dict, List, Any
from sqlite3 import Connection, Cursor
from pathlib import Path
from app.config import Config  # 使用绝对导入

def get_conn(timeout: int = 5) -> Tuple[Connection, Cursor]:
    """获取SQLite数据库连接和游标
    
    此函数创建并返回一个SQLite数据库连接和对应的游标对象。
    如果数据库文件不存在，会自动创建。
    
    Args:
        timeout: 连接超时时间(秒)，默认5秒
    
    Returns:
        Tuple[Connection, Cursor]: 包含(数据库连接, 游标)的元组
        
    Example:
        ```python
        conn, cursor = get_conn()
        try:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        finally:
            conn.close()
        ```
    """
    # 确保数据库目录存在
    db_path = Path(Config.SQLITE_DB)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建连接
    conn = sqlite3.connect(Config.SQLITE_DB, timeout=timeout)
    # 启用外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    # 设置行工厂为字典形式
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

def execute_query(query: str, params: tuple[Any, ...] = (), fetch_all: bool = True) -> Optional[List[Dict[str, Any]]]:
    """执行SQL查询并返回结果
    
    此函数提供了一个简便的方式执行SQL查询，自动处理连接和错误。
    
    Args:
        query: SQL查询语句
        params: 查询参数，用于参数化查询防止SQL注入
        fetch_all: 是否获取所有结果，False则只获取第一行
    
    Returns:
        Optional[List[Dict[str, Any]]]: 查询结果列表，每行为一个字典
        如果查询失败返回None
        
    Example:
        ```python
        # 获取所有用户
        users = execute_query("SELECT * FROM users")
        
        # 获取特定用户
        user = execute_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch_all=False)
        ```
    """
    try:
        conn, cursor = get_conn()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith("SELECT"):
            if fetch_all:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                row = cursor.fetchone()
                return [dict(row)] if row else []
        else:
            conn.commit()
            return [{"rows_affected": cursor.rowcount}]
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()


