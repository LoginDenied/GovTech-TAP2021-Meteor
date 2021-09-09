import pymysql

from temp import *

def create_connection():
    conn = pymysql.connect(
            host=SQL_HOST,
            db=SQL_DB,
            user=SQL_USER,
            password=SQL_PASSWORD
        )
    cursor = conn.cursor()
    return conn, cursor