import pymysql # type: ignore
import os


# Query type
# "SELECT * FROM products;"

def DB_Query(query="SHOW TABLES;", params=None, read_timeout=60):
    # Connect to DB with timeout settings
    db_connect = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'test'),
        port=25060,
        ssl={'ssl': {}},
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        read_timeout=read_timeout,
        write_timeout=10
    )
    try:
        with db_connect.cursor() as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()
            return data
    finally:
        db_connect.close()
        