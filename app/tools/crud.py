from typing import Dict, Any, List, Union, Optional
import json
from app.models.sql_utils import SQLUtils

def execute_sql(params: Union[str, Dict]) -> Dict[str, Any]:
    """执行SQL查询
    
    参数格式 (JSON字符串或字典):
    {
        "query": "SQL查询语句",  // 必需
        "parameters": [],       // 可选: 查询参数
        "timeout": 10           // 可选: 超时时间(秒)
    }

    示例:
    {
        "query": "SELECT * FROM users WHERE id = ?",
        "parameters": [1],
        "timeout": 5
    }

    Args:
        params: 包含SQL查询的参数(字符串或字典)
               - 如果是字符串，必须是有效的JSON格式
               - 必须包含"query"字段
               - "parameters"和"timeout"为可选字段

    Returns:
        执行结果字典
    """
    # 解析参数
    query = ""
    parameters = []
    timeout = None
    
    # 处理字符串参数（JSON格式）
    if isinstance(params, str):
        try:
            # 尝试解析JSON
            params_dict = json.loads(params)
            query = params_dict.get("query", "")
            parameters = params_dict.get("parameters", [])
            timeout = params_dict.get("timeout")
        except json.JSONDecodeError:
            return {"success": False, "message": "无效的JSON格式"}
    # 处理字典参数
    elif isinstance(params, dict):
        query = params.get("query", "")
        parameters = params.get("parameters", [])
        timeout = params.get("timeout")
    else:
        return {"success": False, "message": "无效的参数类型"}
    
    # 验证查询
    if not query:
        return {"success": False, "message": "无效的SQL查询"}
    
    # 根据查询类型确定允许的操作
    query_type = query.strip().upper()
    if query_type.startswith("SELECT"):
        allowed = ['SELECT']
    elif query_type.startswith(("INSERT", "UPDATE", "DELETE")):
        allowed = ['INSERT', 'UPDATE', 'DELETE']
    else:
        allowed = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']
    
    if not SQLUtils.validate_sql(query, allowed):
        return {"success": False, "message": "SQL验证失败"}
    
    # 执行查询
    return SQLUtils.execute_query(query, parameters, timeout)