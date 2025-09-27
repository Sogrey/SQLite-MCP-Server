from fastmcp import FastMCP
# 统一使用基于项目根目录的绝对导入
from app.config import Config
from app.tools.crud import execute_sql

def setup_server():
    """设置并返回MCP服务器实例"""
    # 创建MCP实例
    mcp = FastMCP('sqlite-mcp')
    
    # 注册工具
    mcp.register_tool(execute_sql)
    
    return mcp

def init_database():
    """初始化SQLite数据库文件"""
    import sqlite3
    from pathlib import Path
    
    db_path = Path(Config.SQLITE_DB)
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.close()
        print(f"✅ 已创建数据库文件: {db_path}")

def run_server():
    """启动MCP服务器"""
    # 初始化数据库
    init_database()
    
    mcp = setup_server()
    
    print("🚀 启动 SQLite MCP 服务器...")
    print(f"📊 数据库路径: {Config.SQLITE_DB}")
    print("📋 可用工具:")
    print("  - execute_sql: 执行SQL查询")
    
    # 设置服务器配置 (通过环境变量)
    import os
    os.environ['MCP_HOST'] = Config.MCP_HOST
    os.environ['MCP_PORT'] = str(Config.MCP_PORT)
    
    # 使用字符串参数直接传递transport类型
    transport_map = {
        "stdio": "stdio",
        "sse": "sse",
        "streamable-http": "streamable-http"
    }
    
    print(f"🌐 服务器运行在: http://{Config.MCP_HOST}:{Config.MCP_PORT}")
    mcp.run(transport=transport_map[Config.MCP_SERVER_TYPE])

if __name__ == "__main__":
    import argparse
    import logging
    import socket
    import os
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='SQLite MCP服务器启动参数')
    parser.add_argument("--server_type", choices=["stdio", "sse", "streamable-http"], 
                      default="sse", help="Server type: stdio/sse/streamable-http")
    parser.add_argument("--host", default="0.0.0.0", help="Server host address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()

    # 检查端口占用
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((args.host, args.port))
        sock.close()
    except OSError as e:
        if e.errno == 10048:  # 端口被占用错误码
            logger.error(f"端口 {args.port} 已被占用，请使用其他端口")
            exit(1)
        raise

    # 更新配置
    Config.MCP_SERVER_TYPE = args.server_type
    Config.MCP_HOST = args.host
    Config.MCP_PORT = args.port
    
    # 显示启动信息
    if args.server_type == "stdio":
        logger.info("""
stdio模式已启动，等待标准输入...
调用方式：需要通过其他程序通过标准输入输出流调用
        """)
    elif args.server_type == "sse":
        logger.info(f"""
SSE模式已启动
访问URL: http://{args.host}:{args.port}/sse
测试命令: curl http://{args.host}:{args.port}/sse
        """)
    elif args.server_type == "streamable-http":
        logger.info(f"""
Streamable-HTTP模式已启动
访问URL: http://{args.host}:{args.port}/mcp
测试命令: curl http://{args.host}:{args.port}/mcp
        """)
    
    try:
        run_server()
        logger.info(f"MCP服务器已启动，端口: {args.port}")
    except Exception as e:
        logger.error(f"启动MCP服务器失败: {str(e)}")
        exit(1)
    except KeyboardInterrupt:
        logger.info("MCP服务器已停止")