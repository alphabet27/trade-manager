import sqlite3
import pandas as pd

db_path = "../database/"

def get_connection():
	return sqlite3.connect(db_path + "inventory.db")

def get_queries(key, qfile = "queries.sql"):
	query_file = open(db_path + qfile, "r")
	q_temp = "".join(query_file.readlines()).split('--%' + key + '=')
	return {q.split('\n--%')[0] : q.split('--%\n')[1] for q in q_temp[1:]}

def get_table_columns(db_conn, table_name):
	cursor = db_conn.cursor()
	cursor.execute(f"select * from {table_name};")
	return [d[0] for d in cursor.description]

def get_batch(db_conn, pid=None):
	print(f"Querying batch with PID={pid}")
	if pid is None:
		df = SQL_DataFrame(columns=["SID","BATCH", "EXPIRY", "MRP", "BAL"], from_sql=False)
		return df.set_index("BATCH")
	else:
		df = SQL_DataFrame(con=db_conn, sql=f"select * from stock_db where PID=?", params=(pid,))
		return df.set_index("BATCH")

def increment_stock(db_conn, stock_dict, trsc_type, pop_null=False):
	if trsc_type=="purc":
		stock_dict["QTY"] = -1*stock_dict["QTY"]
	cursor = db_conn.cursor()
	stock_df = get_batch(db_conn, stock_dict["PID"])
	if stock_dict["BATCH"] in list(stock_df.index):
		prev_stock = stock_df.loc[stock_dict["BATCH"]].to_dict()
		prev_stock["BATCH"] = stock_dict["BATCH"]
		print(f"Updating existing record {prev_stock}")
		new_stock = (prev_stock["BAL"] + stock_dict["QTY"], prev_stock["SID"])
		cursor.execute(f"UPDATE stock_db SET BAL=? WHERE SID=?", new_stock)
		print(f"new_stock = {new_stock}")
		print(f"Rows affected = {cursor.rowcount}")
	else:
		temp = dict(stock_dict)
		temp["BAL"] = temp["QTY"]
		del temp["QTY"]
		print(f"Adding new stock = {temp}")
		insert_row(cursor, "stock_db", temp)
	if pop_null:
		cursor.execute(f"DELETE FROM stock_db WHERE BAL=?", (0,))

def deduct_stock(db_conn, stock_dict, trsc_type, pop_null=False):
	stock_dict["QTY"] = -1*stock_dict["QTY"]
	increment_stock(db_conn, stock_dict, trsc_type, pop_null=pop_null)

def add_csv_data(db_conn, file_path, table_name):
	df = pd.read_csv(file_path)
	cursor = db_conn.cursor()
	for i in range(len(df)):
		row = df.iloc[i].to_dict()
		insert_row(cursor, table_name, row)
	db_conn.commit()

def get_transactions_query(trsc_type, fy_id):
	queries = get_queries("view")
	sql = queries["transaction_summary_billno"]
	sql = sql.replace("trsc", trsc_type)
	sql = sql.replace("fy", fy_id)
	return sql

def get_pandas_table(table_name, *args, **kwargs):
	db_conn = get_connection()
	sql = f"select * from {table_name}"
	return SQL_DataFrame(sql, db_conn, *args, **kwargs)

def insert_row(cursor, table_name, row_data):
	q = get_queries("add_to_table")["table_name%new_row"]
	q = q.replace("table_name", table_name)
	q = q.replace("cols", f"({', '.join(list(row_data.keys()))})")
	q = q.replace("new_row", f"({', '.join(['?']*len(row_data))})")
	print(f"Inserting into {table_name} - {list(row_data.values())}")
	cursor.execute(q, tuple(row_data.values()))

class SQL_DataFrame(pd.DataFrame):
	def __init__(self, *args, from_sql=True, **kwargs):
		if from_sql:
			super().__init__(pd.read_sql(*args, **kwargs))
		else:
			if "sql" in kwargs.keys():
				_=kwargs.pop("sql")
				_=kwargs.pop("con")
			super().__init__(*args, **kwargs)

	def scan(self, key, literal, isunique=False):
		if isunique:
			return self[self[key]==literal].iloc[0].to_dict()
		else:
			return SQL_DataFrame(self[self[key]==literal], from_sql=False)

	def id_by_dict(self, row_idx, search_by):
		row_id = dict(row_idx)
		temp = self.scan(search_by[0], row_id[search_by[0]])
		for i in range(len(search_by)):
			key, value = search_by[i], row_id[search_by[i]]
			temp = temp.scan(key, value)
		if len(temp)>1:
			raise Exception("Multiple entries by given condition!!")
		else:
			return int(temp.iloc[0].name)


if __name__=="__main__":
	db_conn = get_connection()
	cursor = db_conn.cursor()
	billdata_cols = SQL_DataFrame("select * from sale_fulldata_fy_25;", db_conn)
	# billdata_cols = SQL_DataFrame('''select s.PID, p.GST_D, p.HSN_CODE, p.MFG,
	# 								p.UNIT, s.BATCH, s.EXPIRY, s.MRP, s.BAL
	# 							FROM
	# 								product_db p
	# 							JOIN
	# 								stock_db s ON p.PID = s.PID
	# 							ORDER BY
	# 								p.PID ASC;''', db_conn)
	#cursor.execute(f"alter table sale_fulldata_fy_25 add column DISC INTEGER CHECK(DISC BETWEEN 0 AND 100);")
	#db_conn.commit()
	#add_csv_data(db_conn, "csv_data/sale_fulldata.csv", "sale_fulldata_fy_25")
	print(billdata_cols)
	db_conn.commit()
	db_conn.close()
