from app.database import get_conn
import re
from typing import List, Dict, Any, Optional, Union

class SQLUtils:
    """通用SQL工具类，提供SQL执行和验证功能"""
    
    @staticmethod
    def validate_sql(query: str, allowed_types: List[str]) -> bool:
        """验证SQL查询的安全性
        
        Args:
            query: SQL查询字符串
            allowed_types: 允许的SQL操作类型列表，如['SELECT', 'INSERT']
            
        Returns:
            bool: 如果查询安全则返回True
        """
        # 提取SQL操作类型
        match = re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|PRAGMA)\s+', 
                         query.upper())
        if not match:
            return False
        
        operation = match.group(1)
        if operation not in [t.upper() for t in allowed_types]:
            return False
        
        # 检查危险操作
        dangerous_patterns = [
            r';\s*DROP\s+', 
            r';\s*TRUNCATE\s+',
            r';\s*ALTER\s+TABLE\s+'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False
                
        return True

    @staticmethod
    def execute_query(query: str, parameters: Optional[List[Any]] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """执行SQL查询并返回结果
        
        Args:
            query: SQL查询字符串
            parameters: 查询参数列表，用于参数化查询防止SQL注入
            timeout: 查询超时时间（秒）
            
        Returns:
            执行结果字典，包含:
            - success: 是否成功
            - message: 结果消息
            - data: 查询结果(仅SELECT)
            - rows_affected: 影响行数
        """
        conn, cursor = get_conn(timeout=int(timeout) if timeout else 5)
        try:
            cursor.execute(query, parameters if parameters else ())
            
            # 判断操作类型
            match = re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE)\s+', query.upper())
            operation = match.group(1) if match else "UNKNOWN"
            
            if operation == "SELECT":
                columns = [desc[0] for desc in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return {
                    "success": True,
                    "operation": operation,
                    "data": data,
                    "rows_affected": len(data)
                }
            else:
                conn.commit()
                return {
                    "success": True,
                    "operation": operation,
                    "rows_affected": cursor.rowcount
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"执行失败: {str(e)}"
            }
        finally:
            conn.close()