from ui_builder import *

db_conn = sqlb.get_connection()

class BasicForm(UIBuilder):
	def __init__(self, parent, db_conn, table_name, title, *args, combo_dict=None, disabled=None, layout_file="layouts/basic_form.json", **kwargs):
		self.parent = parent
		self.db_conn = db_conn
		root = ttk.Frame(parent.notebook)
		entry_cols = sqlb.get_table_columns(db_conn, table_name)
		entry_dict = dict(zip(entry_cols, [""]*len(entry_cols)))
		super().__init__(root, layout_file=layout_file)
		self.layout["custom_frames"]["entry_block"]["entry_dict"] = entry_dict
		self.layout["custom_frames"]["search_block"]["sql_query"] = f"select * from {table_name}"
		self.table_name = table_name
		temp_ptr = self.layout["custom_frames"]["entry_block"]
		temp_ptr["disabled"] = disabled
		if not combo_dict is None:
			for key, value in combo_dict.items():
				temp_ptr["combos"].append(key)
				temp_ptr["entry_dict"][key] = value


	def build(self):
		super().build()
		self.main_form = self.custom_frames["entry_block"]
		self.main_form.labelize()
		self.main_form.relabel()
		self.custom_frames["search_block"].search_box.bind("<Return>", self.load_data)
		self.custom_frames["search_block"].select_button.config(command = self.load_data)
		self.ent_ptr = self.custom_frames["entry_block"]
		self.widgets["mode_label"].config(font=head_font)

	def load_data(self, event=None, **kw):
		sel_ptr = self.custom_frames["search_block"]
		sel_ptr.get_data()
		if sel_ptr.output is None:
			raise Exception("Nothing selected!!")
		temp = dict(sel_ptr.output)
		for key in self.ent_ptr.combos:
			self.ent_ptr.entry_dict[key]["current"] = temp.pop(key)
		self.ent_ptr.entry_dict.update(temp)
		self.ent_ptr.relabel()
		self.ent_ptr.disable_entries()
		self.widgets["mode_label"].config(text = "Idle Mode")

	def on_add(self, enable_all=True):
		self.ent_ptr.clear_entries()
		self.ent_ptr.enable_entries(enable_all = enable_all)
		self.widgets["mode_label"].config(text = " Add Mode")

	def on_edit(self):
		self.load_data()
		self.ent_ptr.enable_entries()
		self.widgets["mode_label"].config(text = "Edit Mode")

	def on_delete(self, key=None):
		self.load_data()
		cursor = self.db_conn.cursor()
		value = self.custom_frames["search_block"].output[key]
		del_query = sqlb.get_queries("delete_row")["table_name"]
		del_query = del_query.replace("table_name", self.table_name)
		del_query = del_query.replace("col_name", key)
		cursor.execute(del_query, (value,))
		self.db_conn.commit()

	def on_save(self, commit=True, data_modif=None, **kw):
		table_name = self.table_name
		data = self.ent_ptr.get_data()
		if not data_modif is None:
			data = data_modif(data, **kw)
		cursor = db_conn.cursor()
		sqlb.insert_row(cursor, table_name, data)
		if commit:
			db_conn.commit()
			self.main_form.disable_entries(disable_all=True)
			self.widgets["mode_label"].config(text = "Idle Mode")

	def on_cancel(self):
		self.root.destroy()

def PartyForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "party_db", title, *args, combo_dict={"ACC_TYPE":{"current":"sale", "values":["sale","purc"]}}, disabled = ["ALIAS"], **kwargs)
	pf.layout["title"] = "Party Form"
	sel_ptr = pf.layout["custom_frames"]["search_block"]
	sel_ptr["sql_query"] += "order by ALIAS"
	sel_ptr["keys"] = ["ALIAS", "PARTY_NAME"]
	ctrl_ptr = pf.layout["frames"]["controls_frame"]["widgets"]
	ctrl_ptr[2]["command_kwargs"]["key"] = "ALIAS"
	temp_ptr = pf.layout["custom_frames"]["entry_block"]
	temp_ptr["shape"] = [7,2]
	pf.build()
	return pf

def ProductForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "product_db", title, *args, disabled = ["PID"], **kwargs)
	sel_ptr = pf.layout["custom_frames"]["search_block"]
	sel_ptr["sql_query"] += "order by PID"
	pf.build()
	return pf

def make_fy(fy_data, sql_conn):
	if not fy_data["FY_ID"].isalnum():
		raise Exception("Cannot create FY!\nNeed Alpha-Numeric FY_ID without space!")
	sqlb.create_fy(sql_conn, fy_data["FY_ID"], fy_data["FY_NAME"])
	return fy_data

def FyForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "fy_list", title, disabled = ["FY_ID"], *args, **kwargs)
	if pf is None:
		return None
	pf.layout["custom_frames"]["search_block"]["keys"] = ["FY_ID", "FY_NAME"]
	ctrl_ptr = pf.layout["frames"]["controls_frame"]["widgets"]
	ctrl_ptr[3]["command_kwargs"]["data_modif"] = make_fy
	ctrl_ptr[3]["command_kwargs"]["sql_conn"] = pf.db_conn
	ctrl_ptr[2]["command_kwargs"]["state"] = "disabled"
	pf.layout["title"] = "FY Form"
	pf.build()
	return pf


if __name__=="__main__":
	import sys
	root = tk.Tk()
	root.notebook = ttk.Notebook(root)
	root.notebook.pack(expand=True, fill="both")
	func_map = {"fy" : ["FyForm", {"root":root,"db_conn":db_conn, "title":"fy modif"}],
				"party" : ["PartyForm", {"root":root,"db_conn":db_conn, "title":"party modif"}],
				"product" : ["ProductForm", {"root":root,"db_conn":db_conn, "title":"prod modif"}],
				}
	func_call = func_map[sys.argv[1]]
	pf = globals()[func_call[0]](**func_call[1])
	root.notebook.add(pf.root)
	pf.root.pack(fill="both", expand=True)
	root.mainloop()
