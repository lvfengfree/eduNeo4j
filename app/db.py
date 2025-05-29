import pymysql
from config import DB_CONFIG


def get_db():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 创建用户表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL
            )
            """)



        conn.commit()
    finally:
        conn.close()