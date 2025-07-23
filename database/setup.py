import sqlite3

def get_queries(sql_file, split_key):
    query_list = ("".join(sql_file.readlines())).split("--%" + split_key + "=")
    queries = {}
    for q in query_list:
        q_list = q.split("--%")
        if len(q_list)>1:
            queries[q_list[0][:-1]] = q_list[1]
    return queries

def create_database(db_path="inventory.db"):
    sql_conn = sqlite3.connect(db_path)
    cursor = sql_conn.cursor()
    #
    sql_file = open("setup.sql", "r")
    queries = get_queries(sql_file, "table")
    for key, value in queries.items():
        cursor.execute(value)
    #
    sql_conn.commit()
    sql_conn.close()
    print("Database Creation Successful!!")

def create_fy(sql_conn, fy_label, fy_name, cursor=None):
    sql_file = open("create_fy.sql", "r")
    queries = get_queries(sql_file, "pattern")
    sql_file.close()
    if cursor is None:
        cursor = sql_conn.cursor()
    for key, value in queries.items():
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {key + fy_label} {value}")
    cursor.execute(f"INSERT OR REPLACE INTO fy_list\nVALUES (?, ?);", (fy_label, fy_name))
    sql_conn.commit()

if __name__ == "__main__":
    create_database()
    sql_conn = sqlite3.connect("inventory.db")
    create_fy(sql_conn, "fy_25", "FY 2025-26")
    sql_conn.close()
