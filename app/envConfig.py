import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'translation')
    MYSQL_CHARSET = 'utf8mb4'
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("BASE_URL")
