# SQLite MCP Server

通用SQLite数据库管理工具，通过MCP协议提供SQL执行能力。

## 功能特性
- 执行任意合法的SQL查询
- 支持SELECT/INSERT/UPDATE/DELETE/CREATE等操作
- 内置SQL注入防护
- 支持SSE和stdio两种通信模式
- 可配置的IP和端口

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

SQLite3 是Python内置模块，无需单独安装。

### 启动服务器
```bash
# 默认配置
python app/main.py

# 自定义配置
# stdio模式
python app/main.py --server_type stdio

# sse模式
python app/main.py --server_type sse --host 0.0.0.0 --port 8000

# streamableHttp模式 
python app/main.py --server_type streamableHttp --host 127.0.0.1 --port 8080
```

### 客户端调用示例
```python
# 查询数据
execute_sql({
    "query": "SELECT * FROM table WHERE condition"
})

# 插入数据  
execute_sql({
    "query": "INSERT INTO table (col1, col2) VALUES (val1, val2)"
})

# 创建表
execute_sql({
    "query": "CREATE TABLE IF NOT EXISTS table (id INTEGER PRIMARY KEY, name TEXT)"
})
```

## 配置与启动

### 启动参数
| 参数 | 默认值 | 描述 |
|------|--------|------|
| --server_type | sse | 服务器类型: stdio/sse/streamable-http |
| --host | 0.0.0.0 | 监听地址 |
| --port | 8000 | 监听端口 |
| --log_level | INFO | 日志级别: DEBUG/INFO/WARNING/ERROR |

### 环境变量配置
| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| MCP_HOST | 0.0.0.0 | 监听地址 |
| MCP_PORT | 8000 | 监听端口 |
| MCP_SERVER_TYPE | sse | 服务器类型 (sse/stdio/streamable-http) |

### 数据库自动创建
服务启动时会自动在项目根目录创建`data/demo.db`数据库文件（如果不存在）

### 启动示例
```bash
# SSE模式 (默认)
python app/main.py --server_type sse --port 8000

# stdio模式
python app/main.py --server_type stdio

# streamable-http模式 (注意使用短横线)
python app/main.py --server_type streamable-http --port 8080

# 带调试日志
python app/main.py --log_level DEBUG
```

### JSON配置示例

#### stdio模式配置
```json
{
  "mcpServers": {
    "sqlite-mcp": {
      "command": "python",
      "args": ["app/main.py", "--server_type", "stdio"]
    }
  }
}
```

#### sse模式配置
```json
{
  "mcpServers": {
    "sqlite-mcp": {
      "type": "sse",
      "url": "http://localhost:8000/sse",
      "port": 8000
    }
  }
}
```

#### streamable-http模式配置
```json
{
  "mcpServers": {
    "sqlite-mcp": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp",
      "port": 8000,
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

## 项目结构
```
SQLite-MCP-Server/
├── app/                 # 主应用代码
│   ├── main.py          # 主入口
│   ├── database.py      # 数据库连接  
│   ├── models/          # 数据模型
│   └── tools/           # MCP工具
├── config.py            # 配置管理
└── requirements.txt    # 依赖列表