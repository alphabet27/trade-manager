from ui_builder import *

db_conn = sqlb.get_connection()

class TransactionForm(UIBuilder):
	def __init__(self, parent, db_conn, billdata, trsc_data, trsc_type, fy_id, title, add_mode=False, *args, **kwargs):
		self.table_name = f"{trsc_type}_fulldata_{fy_id}"
		main_kw = dict(parent = parent, db_conn = db_conn, billdata = billdata, trsc_data = trsc_data, trsc_type = trsc_type, fy_id = fy_id, title = title, add_mode=add_mode)
		for key,value in main_kw.items():
			setattr(self, key, value)
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file = "layouts/transaction_form.json")
		entry_cols = sqlb.get_table_columns(db_conn, self.table_name)
		entry_dict = dict(zip(entry_cols, [""]*len(entry_cols)))
		entry_dict.update(self.trsc_data)
		entry_dict.update({"BATCH":{"current":trsc_data["BATCH"], "values":[trsc_data["BATCH"]]}, "BAL":""})
		temp_ptr = self.layout["custom_frames"]["entry_block"]
		temp_ptr.update(dict(combos = ["BATCH"], entry_dict = entry_dict))
		temp_ptr["disabled"] = ["TID", "BILL", "SR_NO", "PID", "EXPIRY", "MFG", "MRP", "BAL"]
		if not add_mode:
			self.prev_data = dict(PID = trsc_data["PID"], QTY = trsc_data["QTY"], BATCH = trsc_data["BATCH"], EXPIRY = trsc_data["EXPIRY"], MRP = trsc_data["MRP"])
			sqlb.increment_stock(self.db_conn, self.prev_data, self.trsc_type)
		self.root.grid_columnconfigure(2, weight=1)
		self.build()

	def build(self):
		super().build()
		pid, alias = (self.trsc_data["PID"], self.billdata["ALIAS"])
		for key, value in {"search_block":["PID", pid], "history_party_sel":["ALIAS", alias], "history_fy_sel":["FY_ID", self.fy_id]}.items():
			sel_ptr = self.custom_frames[key]
			sel_ptr.search_box.bind("<Return>", self.load_data)
			sel_ptr.select_button.config(command = self.load_data)
			sel_ptr.current_key.set(value[0])
			sel_ptr.search_box.set(value[1])
		#
		self.widgets["mode_label"].config(font=head_font)
		self.widgets["history_label"].config(font=head_font)
		#
		self.main_form = self.custom_frames["entry_block"]
		self.main_form.labelize()
		self.main_form.relabel()
		self.main_form.BATCH_e.bind("<FocusOut>", self.load_batch)
		if not self.add_mode:
			self.load_data()

	def on_save(self, also_commit=False):
		cursor = self.db_conn.cursor()
		row_data = self.main_form.get_data()
		if self.add_mode:
			del row_data["TID"]
		stock_data = dict(PID = row_data["PID"], QTY = int(row_data["QTY"]), BATCH = row_data["BATCH"], EXPIRY = row_data["EXPIRY"], MRP = row_data["MRP"])
		sqlb.deduct_stock(self.db_conn, stock_data, self.trsc_type, pop_null=True)
		for key in list(row_data.keys()):
			if key in ["BAL", "MFG", "UNIT"]:
				del row_data[key]
				#del row_data["BAL"], row_data["MFG"], row_data["UNIT"]
		sqlb.insert_row(self.db_conn, self.table_name, row_data)
		if also_commit:
			self.db_conn.commit()
		print("Saving product with savepoints = ",sqlb.get_savepoints(self.db_conn))
		self.db_conn.execute("RELEASE SAVEPOINT trsc_form;")
		print("Saved product with savepoints = ",sqlb.get_savepoints(self.db_conn))
		self.root.destroy()

	def quick_add(self):
		self.custom_frames["search_block"].get_data()
		pid = self.custom_frames["search_block"].output["PID"]
		batch_root = tk.Toplevel(self.root)
		batch_root.title("Add Batch")
		batch_data = {"PID":pid, "BATCH":"", "EXPIRY":"", "MRP":"", "BAL":""}
		batch_wb = widget_block(batch_root, batch_data, disabled=["PID"])
		batch_wb.grid(row=0, column=0)
		batch_wb.labelize()
		batch_wb.relabel()
		def add_batch(wb, root):
			bd = wb.get_data()
			sqlb.insert_row(self.db_conn, "stock_db", bd)
			root.destroy()
		add_bn = tk.Button(batch_root, text="Add", command=lambda:add_batch(batch_wb, batch_root))
		add_bn.grid(row = 0, column=1, padx=5, ipadx=5, sticky="sw")
		batch_root.mainloop()

	def on_cancel(self):
		print("Discarding changes with savepoints = ",sqlb.get_savepoints(self.db_conn))
		self.db_conn.execute("ROLLBACK to SAVEPOINT trsc_form;")
		self.db_conn.execute("RELEASE SAVEPOINT trsc_form;")
		print("Discarding changes with savepoints = ",sqlb.get_savepoints(self.db_conn))
		self.root.destroy()

	def load_data(self, event=None, **kw):
		old_data = self.main_form.get_data()
		self.custom_frames["search_block"].get_data()
		data = dict(self.custom_frames["search_block"].output)
		self.main_form.entry_dict["PID"] = data["PID"]
		self.main_form.entry_dict["GST"] = data["GST_D"]
		for key in ["QTY", "RATE", "DISC", "GST"]:
			self.main_form.entry_dict[key] = old_data[key]
		self.load_batch()
		self.load_history(data["PID"])

	def load_batch(self, event=None):
		old_data = self.main_form.get_data()
		self.custom_frames["search_block"].get_data()
		data = dict(self.custom_frames["search_block"].output)
		pid = data["PID"]
		self.stock_df = sqlb.get_batch(self.db_conn, pid)
		batch = self.custom_frames["entry_block"].BATCH_e.get()
		batch_ptr = self.main_form.entry_dict["BATCH"]
		batch_ptr["values"] = list(self.stock_df.index)
		if not batch in batch_ptr["values"]:
			batch = ""
		batch_ptr["current"] = batch
		if batch!="":
			vals = self.stock_df.loc[batch].to_dict()
			del vals["SID"]
			self.main_form.entry_dict.update(vals)
		else:
			self.main_form.entry_dict.update({"EXPIRY":"", "MRP":"", "BAL":""})
		for key in ["QTY", "RATE", "DISC", "GST"]:
			self.main_form.entry_dict[key] = old_data[key]
		self.main_form.relabel()

	def load_history(self, pid):
		kw = dict(alias=None, fy_id = None)
		for frame_name, key in [("history_party_sel", "ALIAS"), ("history_fy_sel", "FY_ID")]:
			self.custom_frames[frame_name].get_data()
			kw[key.lower()] = self.custom_frames[frame_name].output[key]
		df = sqlb.get_history(self.db_conn, self.trsc_type, pid, **kw)
		self.custom_frames["history_block"].data = df
		self.custom_frames["history_block"].refill_table()


if __name__=="__main__":
	root = tk.Tk()
	root.notebook = ttk.Notebook(root)
	root.notebook.pack(expand=True, fill="both")
	transaction_data = {"parent":root, "billdata":{"BILL":1, "ALIAS":"Sujay"}, "title":"trsc modif", "trsc_data":{"PID":"id17", "QTY":10, "EXPIRY":"10/2026", "MRP":100, "BATCH":"-----"}, "trsc_type":"sale", "fy_id":"fy_25","db_conn":db_conn}
	pf = TransactionForm(**transaction_data)
	root.notebook.add(pf.root)
	pf.root.pack(fill="both", expand=True)
	root.mainloop()
