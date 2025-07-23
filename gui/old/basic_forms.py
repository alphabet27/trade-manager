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


	def build(self, data_modif=None):
		if data_modif is None:
			data_modif = lambda data:data
		super().build()
		self.main_form = self.custom_frames["entry_block"]
		self.main_form.labelize()
		self.main_form.relabel()
		self.custom_frames["search_block"].search_box.bind("<Return>", lambda event = None: self.load_data(data_modif=data_modif))
		self.custom_frames["search_block"].select_button.config(command = lambda : self.load_data(data_modif=data_modif))
		self.ent_ptr = self.custom_frames["entry_block"]
		self.widgets["mode_label"].config(font=head_font)

	def load_data(self, event=None, data_modif=None, **kw):
		sel_ptr = self.custom_frames["search_block"]
		sel_ptr.get_data()
		if sel_ptr.output is None:
			raise Exception("Nothing selected!!")
		temp = dict(sel_ptr.output)
		if not data_modif is None:
			temp = data_modif(temp, **kw)
		for key in self.ent_ptr.combos:
			self.ent_ptr.entry_dict[key] = temp.pop(key)
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

	def on_delete(self):
		print(f"Define delete from {self.table_name}")

	def on_save(self, commit=True, data_modif=None, **kw):
		table_name = self.table_name
		data = self.ent_ptr.get_data()
		if not data_modif is None:
			data = data_modif(data, **kw)
		cursor = db_conn.cursor()
		sqlb.insert_row(cursor, table_name, data)
		if commit:
			db_conn.commit()

	def on_cancel(self):
		self.root.destroy()

def get_acctype(data):
	curr_type = data.pop("ACC_TYPE")
	data["ACC_TYPE"] = {"current":curr_type, "values":["sale","purc"]}
	return data

def PartyForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "party_db", title, *args, combo_dict={"ACC_TYPE":{"current":"sale", "values":["sale","purc"]}}, disabled = ["ALIAS"], **kwargs)
	pf.layout["title"] = "Party Form"
	temp_ptr = pf.layout["custom_frames"]["search_block"]
	temp_ptr["keys"] = ["ALIAS", "PARTY_NAME"]
	temp_ptr = pf.layout["custom_frames"]["entry_block"]
	temp_ptr["shape"] = [7,2]
	pf.build(data_modif = get_acctype)
	return pf

def ProductForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "product_db", title, *args, disabled = ["PID"], **kwargs)
	pf.build()
	return pf

def make_fy(fy_data):
	print(f"Make FY as \n{fy_data}")
	return fy_data

def FyForm(root, db_conn, title, *args, **kwargs):
	pf = BasicForm(root, db_conn, "fy_list", title, disabled = ["FY_ID"], *args, **kwargs)
	if pf is None:
		return None
	pf.layout["custom_frames"]["search_block"]["keys"] = ["FY_ID", "FY_NAME"]
	ctrl_ptr = pf.layout["frames"]["controls_frame"]["widgets"]
	ctrl_ptr[3]["command_kwargs"]["data_modif"] = make_fy
	pf.layout["title"] = "FY Form"
	pf.build()
	return pf

class TransactionForm(BasicForm):
	def __init__(self, parent, db_conn, billdata, trsc_data, trsc_type, fy_id, title, *args, **kwargs):
		trsc_name = f"{trsc_type}_fulldata_{fy_id}"
		self.fy_id = fy_id
		self.trsc_type = trsc_type
		self.trsc_data = trsc_data
		super().__init__(parent, db_conn, trsc_name, title, *args, layout_file="layouts/transaction_form.json", disabled = ["TID", "BILL", "SR_NO", "PID", "EXPIRY", "MRP"], combo_dict = {"BATCH":{"current":self.trsc_data["BATCH"], "values":[]}}, **kwargs)
		self.layout["custom_frames"]["search_block"]["sql_query"] = f"select * from product_db;"
		self.root.grid_columnconfigure(2, weight=1)
		self.build()

	def build(self):
		super().build()
		self.main_form.entry_dict.update(self.trsc_data)
		self.widgets["history_label"].config(font = head_font)
		self.custom_frames["search_block"].current_key.set("PID")
		self.custom_frames["search_block"].search_box.set(self.main_form.entry_dict["PID"])
		self.custom_frames["history_fy_sel"].search_box.bind("<Return>", self.load_history)
		self.custom_frames["history_fy_sel"].select_button.config(command = self.load_history)
		self.custom_frames["history_party_sel"].search_box.bind("<Return>", self.load_history)
		self.custom_frames["history_party_sel"].select_button.config(command = self.load_history)

	def load_trsc(self, data):
		return data

	def load_data(self, event=None, data_modif=None, **kw):
		super().load_data(event=event, data_modif = self.load_trsc, **kw)
		self.load_history()

	def load_history(self):
		print("Define load history")

if __name__=="__main__":
	import sys
	root = tk.Tk()
	root.notebook = ttk.Notebook(root)
	root.notebook.pack(expand=True, fill="both")
	func_map = {"fy" : ["FyForm", {"root":root,"db_conn":db_conn, "title":"fy modif"}],
				"party" : ["PartyForm", {"root":root,"db_conn":db_conn, "title":"party modif"}],
				"product" : ["ProductForm", {"root":root,"db_conn":db_conn, "title":"prod modif"}],
				"transaction":["TransactionForm", {"parent":root, "billdata":{"BILL":1, "ALIAS":"Sujay"}, "title":"trsc modif", "trsc_data":{"PID":"id06", "BATCH":""}, "trsc_type":"sale", "fy_id":"fy_25","db_conn":db_conn}]}
	func_call = func_map[sys.argv[1]]
	pf = globals()[func_call[0]](**func_call[1])
	if sys.argv[1]=="transaction":
		pf.build()
	root.notebook.add(pf.root)
	pf.root.pack(fill="both", expand=True)
	root.mainloop()
