#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLite MCP 客户端示例
=====================

此文件演示如何连接和使用SQLite MCP服务器的不同方式。
支持三种连接模式：stdio、SSE和streamable-http。

使用方法:
1. 确保服务器已启动
2. 根据服务器启动模式选择对应的客户端连接方式
3. 执行SQL查询并处理结果
"""

import json
import requests
import subprocess
import sys
import os
from typing import Dict, Any, List, Union, Optional

# 配置参数
SERVER_HOST = "localhost"
SERVER_PORT = 8000
SERVER_TYPE = "sse"  # 可选: "stdio", "sse", "streamable-http"


class SQLiteMCPClient:
    """SQLite MCP 客户端类，支持多种连接方式"""
    
    def __init__(self, server_type: str = "sse", host: str = "localhost", port: int = 8000):
        """初始化客户端
        
        Args:
            server_type: 服务器类型，支持 "stdio", "sse", "streamable-http"
            host: 服务器主机地址
            port: 服务器端口
        """
        self.server_type = server_type
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.process = None
        
        # 如果是stdio模式，启动服务器进程
        if server_type == "stdio":
            self._start_stdio_server()
    
    def _start_stdio_server(self):
        """启动stdio模式的服务器进程"""
        try:
            # 启动服务器进程
            self.process = subprocess.Popen(
                ["python", "app/main.py", "--server_type", "stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("已启动stdio模式服务器进程")
        except Exception as e:
            print(f"启动stdio服务器失败: {e}")
            sys.exit(1)
    
    def execute_sql(self, query: str, parameters: Optional[List[Any]] = None, 
                   timeout: Optional[int] = None) -> Dict[str, Any]:
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            parameters: 查询参数列表
            timeout: 查询超时时间(秒)
            
        Returns:
            Dict: 查询结果
        """
        # 构建请求参数
        params = {
            "query": query
        }
        if parameters:
            params["parameters"] = parameters
        if timeout:
            params["timeout"] = timeout
            
        # 根据不同连接方式执行查询
        if self.server_type == "stdio":
            return self._execute_stdio(params)
        elif self.server_type == "sse":
            return self._execute_sse(params)
        elif self.server_type == "streamable-http":
            return self._execute_http(params)
        else:
            raise ValueError(f"不支持的服务器类型: {self.server_type}")
    
    def _execute_stdio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """通过stdio模式执行查询"""
        if not self.process:
            raise RuntimeError("stdio服务器进程未启动")
            
        # 构建MCP请求
        request = {
            "type": "execute",
            "tool": "execute_sql",
            "params": params
        }
        
        # 发送请求到服务器进程
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # 读取响应
        response = self.process.stdout.readline()
        try:
            result = json.loads(response)
            return result.get("result", {})
        except json.JSONDecodeError:
            return {"success": False, "message": "解析响应失败"}
    
    def _execute_sse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """通过SSE模式执行查询"""
        url = f"{self.base_url}/sse"
        
        # 构建MCP请求
        request = {
            "type": "execute",
            "tool": "execute_sql",
            "params": params
        }
        
        try:
            response = requests.post(url, json=request)
            if response.status_code == 200:
                # SSE响应需要解析事件流
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        try:
                            result = json.loads(data)
                            if result.get("type") == "result":
                                return result.get("result", {})
                        except json.JSONDecodeError:
                            continue
                return {"success": False, "message": "未收到有效响应"}
            else:
                return {"success": False, "message": f"HTTP错误: {response.status_code}"}
        except requests.RequestException as e:
            return {"success": False, "message": f"请求错误: {str(e)}"}
    
    def _execute_http(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """通过streamable-http模式执行查询"""
        url = f"{self.base_url}/mcp"
        
        # 构建MCP请求
        request = {
            "type": "execute",
            "tool": "execute_sql",
            "params": params
        }
        
        try:
            response = requests.post(url, json=request)
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("type") == "result":
                        return result.get("result", {})
                    return {"success": False, "message": "未收到有效响应"}
                except json.JSONDecodeError:
                    return {"success": False, "message": "解析响应失败"}
            else:
                return {"success": False, "message": f"HTTP错误: {response.status_code}"}
        except requests.RequestException as e:
            return {"success": False, "message": f"请求错误: {str(e)}"}
    
    def close(self):
        """关闭客户端连接"""
        if self.server_type == "stdio" and self.process:
            self.process.terminate()
            self.process = None


def main():
    """主函数，演示客户端使用方法"""
    # 从环境变量或命令行参数获取配置
    server_type = os.environ.get("MCP_SERVER_TYPE", SERVER_TYPE)
    host = os.environ.get("MCP_HOST", SERVER_HOST)
    port = int(os.environ.get("MCP_PORT", SERVER_PORT))
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        server_type = sys.argv[1]
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    
    # 创建客户端实例
    client = SQLiteMCPClient(server_type, host, port)
    
    try:
        # 示例1: 创建表
        print("\n创建表:")
        result = client.execute_sql("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER
        )
        """)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 示例2: 插入数据
        print("\n插入数据:")
        result = client.execute_sql(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            ["张三", "zhangsan@example.com", 30]
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 示例3: 查询数据
        print("\n查询数据:")
        result = client.execute_sql("SELECT * FROM users")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 示例4: 更新数据
        print("\n更新数据:")
        result = client.execute_sql(
            "UPDATE users SET age = ? WHERE name = ?",
            [31, "张三"]
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 示例5: 再次查询
        print("\n再次查询:")
        result = client.execute_sql("SELECT * FROM users")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"执行出错: {e}")
    finally:
        # 关闭客户端
        client.close()


if __name__ == "__main__":
    main()