import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "demo.db"

class Config:
    MCP_SERVER_TYPE = os.getenv("MCP_SERVER_TYPE", "sse")
    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")  # 默认监听所有接口
    MCP_PORT = int(os.getenv("MCP_PORT", 8000))
    SQLITE_DB = str(DB_PATH)