import pymysql

def create_connection(config):
    conn = pymysql.connect(
        host=config["SQL_HOST"],
        db=config["SQL_DB"],
        user=config["SQL_USER"],
        password=config["SQL_PASSWORD"]
    )
    cursor = conn.cursor()
    return conn, cursor