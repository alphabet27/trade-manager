import json

# load_database has to append db_path to each entry of database.json

def load_database(db_path):
	database = json.load(open(db_path + 'database.json','r'))
	i=0
	while not (type(tab_path) is str):
		for db_table, tab_path in database.items():
			database[db_table] = db_path + tab_path
