from ui_builder import *
from tkinter import messagebox
import tkinter.filedialog as filedialog

db_conn = sqlb.get_connection()
fy_query_str = "select * from fy_list order by FY_NAME;"

fy_dict = sqlb.SQL_DataFrame(fy_query_str, db_conn, index_col=["FY_ID"]).to_dict()["FY_NAME"]

def get_ledger_data(trsc_type, fy_id, alias):
	queries = sqlb.get_queries('view')
	ldr_query = queries['ledger_alias']
	ldr_query = ldr_query.replace("fulldata_table", f"{trsc_type}_fulldata_{fy_id}")
	ldr_query = ldr_query.replace("billdata_table", f"{trsc_type}_billdata_{fy_id}")
	ldr_query = ldr_query.replace("payments_table", f"{trsc_type}_payments_{fy_id}")
	df = sqlb.SQL_DataFrame(con = db_conn, sql=ldr_query, params=(alias, alias))
	df["Date"] = sqlb.pd.to_datetime(df["Date"], dayfirst=True)
	df = df.sort_values(["Date","BILL/PAY_ID"], ascending=True)
	df["Date"] = df["Date"].dt.date
	return df

def get_hsn_summary(trsc_type, fy_id):
	queries = sqlb.get_queries('view')
	hsn_query = queries['hsn_summary_view']
	hsn_query = hsn_query.replace("fulldata_table", f"{trsc_type}_fulldata_{fy_id}")
	hsn_query = hsn_query.replace("billdata_table", f"{trsc_type}_billdata_{fy_id}")
	df = sqlb.SQL_DataFrame(con = db_conn, sql=hsn_query)
	df["INVOICE_DATE"] = sqlb.pd.to_datetime(df["INVOICE_DATE"], dayfirst=True)
	df["INVOICE_DATE"] = df["INVOICE_DATE"].dt.date
	return df

class Ledger(UIBuilder):
	def __init__(self, parent, trsc_type, db_conn, title, **kw):
		self.parent = parent
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/ledger_view.json")
		self.layout["title"] = title
		self.db_conn = db_conn
		self.trsc_type = trsc_type
		if trsc_type=='purc':
			query_ptr = self.layout["custom_frames"]["search_block"]["sql_query"]
			query_ptr = query_ptr.replace('sale', 'purc')
		self.current_fy = tk.StringVar(root, value="")
		self.fy_current = ""
		fr_ptr = self.layout["frames"]["fy_select"]["widgets"]
		for i, fy_id in enumerate(fy_dict.keys()):
			fr_ptr.append({"class": "Radiobutton",
						   "text" : fy_dict[fy_id],
						   "variable" : "current_fy",
						   "value" : fy_id,
						   "command": "validate",
						   "command_kwargs":{},
						   "grid":{"row":i+1, "column":0}})
		self.child_tabs = []
		self.build()
		#
		self.custom_frames["search_block"].search_box.bind("<Return>", self.toogle_fy)
		self.custom_frames["search_block"].select_button.config(command=self.toogle_fy)

	def validate(self, loud=False):
		validity = (self.current_fy.get() == self.fy_current)
		if loud:
			return validity
		else:
			pass

	def add_tab(self, data, **kw):
		data["FY_ID"] = self.current_fy.get()
		self.custom_frames["search_block"].get_data()
		if self.custom_frames["search_block"].output is None:
			messagebox.showerror("Error", "Please select a Party!")
			return
		alias = self.custom_frames["search_block"].output["ALIAS"]
		data["ALIAS"] = alias
		if len(self.child_tabs)!=0:
			messagebox.showerror("Error", "Found open Sub-Modules!")
			return
		tab_class = {"sale":{"class":"SalePaymentForm",
							 "title":"Record Sale Payment"},
					 "purc":{"class":"PurchasePaymentForm",
							 "title":"Record Purchase Payment"}}[self.trsc_type]
		self.parent._open_tab(f"{tab_class['class']}", title = tab_class['title'], data = data, no_bind=True, **kw)
		self.child_tabs.append(self.parent.tab_instances[tab_class["title"]])
		self.child_tabs[0].root.bind("<Destroy>", lambda e, t=tab_class["title"]: self._on_tab_close(t))

	def on_add(self):
		data = {"PAY_ID":"", "PAY_DATE":"", "AMOUNT":"",
				"PAY_MODE":"", "REMARKS":""}
		self.add_tab(data)

	def on_edit(self):
		tr_data = self.custom_frames["create_treeview"].get_current(search_by = ["PAY_ID"], get_raw = True)
		fy_id = self.current_fy.get()
		if not self.validate(loud=True):
			messagebox.showerror("Error", "Please Refresh!")
			return
		if tr_data["Type"]=="Payment":
			pay_data = sqlb.get_dict(self.db_conn, f"{self.trsc_type}_payments_{self.current_fy.get()}", "PAY_ID", tr_data["BILL/PAY_ID"])
			self.add_tab(data = pay_data, mode = "edit")
		else:
			messagebox.showwarning("Note", "Edit Invoice from Transactions Tab!")
			return


	def on_delete(self):
		cnf = messagebox.askyesnocancel("Warning!", "Confirm Delete Action?")
		if cnf:
			cursor = self.db_conn.cursor()
			q = f"DELETE FROM {self.trsc_type}_payments_{self.fy_id} WHERE PAY_ID=?"
			tr_data = self.custom_frames["create_treeview"].get_current(search_by=["PAY_ID"], get_raw=True)
			if tr_data["Type"]=="Payment":
				cursor.execute(q, (tr_data["PAY_ID"],))
				self.db_conn.commit()
				self.on_refresh()
			else:
				messagebox.showwarning("Note", "Edit Invoice from Transactions Tab!")
				return
		else:
			return

	def on_export(self):
		csv_files = [("CSV Files", "*.csv")]
		self.custom_frames["search_block"].get_data()
		alias = self.custom_frames["search_block"].output["ALIAS"]
		fd = filedialog.asksaveasfile(initialdir=f'../reports/Ledger_{self.trsc_type}', filetypes=csv_files, defaultextension=csv_files, initialfile=f"{alias}_{self.current_fy.get()}.csv")
		if not fd is None:
			self.custom_frames["create_treeview"].data.to_csv(fd, index=False)
		else:
			print("Recieved None!!")

	def toogle_fy(self, event=None):
		fy_id = self.current_fy.get()
		self.fy_current = str(fy_id)
		self.custom_frames["search_block"].get_data()
		alias = self.custom_frames["search_block"].output["ALIAS"]
		if fy_id=="":
			messagebox.showerror("Error", "No FY Selected!")
			return
		elif alias is None:
			messagebox.showerror("Error", "No Party Selected!")
			return
		curr_data = get_ledger_data(self.trsc_type, fy_id, alias)
		self.custom_frames["create_treeview"].data = curr_data
		self.custom_frames["create_treeview"].refill_table()
		self.root.update()

	def on_close(self):
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules?")
			if cnf:
				self.child_tabs[0].on_cancel()
			else:
				return
		self.root.destroy()

	def _on_tab_close(self, title):
		self.parent._on_tab_close(title)
		self.child_tabs = []
		self.toogle_fy()

def SaleLedger(parent, db_conn, title, **kw):
	return Ledger(parent, "sale", db_conn, title, **kw)

def PurcLedger(parent, db_conn, title, **kw):
	return Ledger(parent, "purc", db_conn, title, **kw)


class HSNLedger(UIBuilder):
	def __init__(self, parent, trsc_type, db_conn, title, **kw):
		self.parent = parent
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/hsn_summary_view.json")
		self.layout["title"] = title
		self.db_conn = db_conn
		self.trsc_type = trsc_type
		self.current_fy = tk.StringVar(root, value="")
		self.fy_current = ""
		fr_ptr = self.layout["frames"]["fy_select"]["widgets"]
		for i, fy_id in enumerate(fy_dict.keys()):
			fr_ptr.append({"class": "Radiobutton",
						   "text" : fy_dict[fy_id],
						   "variable" : "current_fy",
						   "value" : fy_id,
						   "command": "toogle_fy",
						   "command_kwargs":{},
						   "grid":{"row":i+1, "column":0}})
		self.child_tabs = []
		self.build()

	def toogle_fy(self, event=None):
		fy_id = self.current_fy.get()
		self.fy_current = str(fy_id)
		if fy_id=="":
			messagebox.showerror("Error", "No FY Selected!")
			return
		curr_data = get_hsn_summary(self.trsc_type, fy_id)
		self.custom_frames["create_treeview"].data = curr_data
		self.custom_frames["create_treeview"].refill_table()
		self.root.update()

	def on_export(self):
		csv_files = [("CSV Files", "*.csv")]
		fd = filedialog.asksaveasfile(initialdir=f'../reports/HSN_Summary_{self.trsc_type}', filetypes=csv_files, defaultextension=csv_files, initialfile=f"{self.current_fy.get()}.csv")
		if not fd is None:
			self.custom_frames["create_treeview"].data.to_csv(fd, index=False)
		else:
			print("Recieved None!!")

	def on_close(self):
		self.root.destroy()

def Sale_HSN_Summary(parent, db_conn, title, **kw):
	return HSNLedger(parent, "sale", db_conn, title, **kw)

def Purchase_HSN_Summary(parent, db_conn, title, **kw):
	return HSNLedger(parent, "purc", db_conn, title, **kw)
