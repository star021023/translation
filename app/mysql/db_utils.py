import mysql.connector
from mysql.connector import Error
from flask import g
from app.envConfig import Config


def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                charset=Config.MYSQL_CHARSET
            )
            print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败: {e}")
            raise
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        print("数据库连接已关闭")


def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS terms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            number VARCHAR(20) NOT NULL,
            chinese VARCHAR(255) NOT NULL,
            english VARCHAR(255) NOT NULL,
            definition TEXT,
            note TEXT,
            UNIQUE KEY unique_term (chinese, english)
        )
        """
        try:
            cursor.execute(create_table_query)
            db.commit()
            print("数据表已初始化")
        except Error as e:
            print(f"初始化表失败: {e}")
            db.rollback()
        finally:
            cursor.close()
