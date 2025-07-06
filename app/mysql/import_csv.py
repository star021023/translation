import csv
import mysql
from mysql.connector import Error
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yxy20021023qaz",
    "database": "translation",
    "charset": "utf8mb4"
}


def import_csv(csv_file):
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # 开启事务（保证数据一致性）
        conn.start_transaction()

        # 读取并导入数据
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # 处理空值
                note = row['注释'].strip() if row['注释'].strip() else None
                definition = row['定义'].strip() if row['定义'].strip() else None

                # 执行插入（使用 IGNORE 跳过重复项）
                cursor.execute(
                    """INSERT IGNORE INTO terms 
                    (number, chinese, english, definition, note)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (row['编号'], row['中文'], row['英语'], definition, note)
                )

        # 4. 提交事务
        conn.commit()
        print(f"成功插入 {cursor.rowcount} 条记录")

    except Error as e:
        print(f"导入失败: {e}")
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    csv_path = "C:\\Users\\yxy\\PycharmProjects\\pythonProject\\app\\resources\\output.csv"
    import_csv(csv_path)
