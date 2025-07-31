from ui_builder import *
import tkinter.filedialog as filedialog

db_conn = sqlb.get_connection()

fy_query_str = "select * from fy_list order by FY_NAME;"
trsc_query_str = sqlb.get_queries("view")["trsc_summary_fy_new"]

def get_trsc_data(trsc_type, fy_id):
	cursor = db_conn.cursor()
	q1 = trsc_query_str.replace("trsc", trsc_type)
	q1 = q1.replace("fy", fy_id)
	#print(f"Executing query {q1}")
	return sqlb.SQL_DataFrame(sql=q1, con=db_conn)

fy_dict = sqlb.SQL_DataFrame(fy_query_str, db_conn, index_col=["FY_ID"]).to_dict()["FY_NAME"]

class SummaryView(UIBuilder):
	def __init__(self, parent, trsc_type, db_conn, title):
		self.parent = parent
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/summary_view.json")
		self.layout["title"] = title
		self.db_conn = db_conn
		self.trsc_type = trsc_type
		self.current_fy = tk.StringVar(root)
		fr_ptr = self.layout["frames"]["fy_select"]["widgets"]
		for i, fy_id in enumerate(fy_dict.keys()):
			fr_ptr.append({"class": "Radiobutton",
						   "text" : fy_dict[fy_id],
						   "variable" : "current_fy",
						   "value" : fy_id,
						   "command": "toogle_fy",
						   "command_kwargs":{},
						   "grid":{"row":i+1, "column":0}})
		self.build()
		self.table_ptr = self.custom_frames["create_treeview"]
		self.child_tabs = []
		#self.root.grid_rowconfigure(1, weight=1)

	def add_tab(self, title, billdata, **kw):
		if len(self.child_tabs)!=0:
			raise Exception("Found open Sub-Modules!")
			return
		self.parent._open_tab("InvoiceView", title = title, billdata = billdata, trsc_type = self.trsc_type, fy_id = self.current_fy.get(), no_bind=True, **kw)
		self.child_tabs.append(self.parent.tab_instances[title])
		self.child_tabs[0].root.bind("<Destroy>", lambda e, t=title: self._on_tab_close(t))

	def on_add(self):
		if len(self.table_ptr.data)>0:
			new_billno = int(self.table_ptr.data["BILL"].max() + 1)
		else:
			new_billno = 1
		self.add_tab("Add Mode", billdata = {"BILL":new_billno, "ALIAS":""}, add_mode=True)

	def on_view(self):
		fy_id = self.current_fy.get()
		table_name = f"{self.trsc_type}_billdata_{fy_id}"
		billdata = self.table_ptr.get_current(search_by=["BILL"])
		billdata = sqlb.get_dict(self.db_conn, table_name, "BILL", billdata["BILL"])
		self.add_tab("View Mode", billdata, view_mode=True)

	def on_edit(self):
		fy_id = self.current_fy.get()
		table_name = f"{self.trsc_type}_billdata_{fy_id}"
		billdata = self.table_ptr.get_current(search_by=["BILL"])
		billdata = sqlb.get_dict(self.db_conn, table_name, "BILL", billdata["BILL"])
		self.add_tab("Edit Mode", billdata)

	def on_delete(self):
		raise Exception("Cannot Delete! Not defined")

	def on_export(self):
		csv_files = [("CSV Files", "*.csv")]
		fd = filedialog.asksaveasfile(initialdir=f'../reports/FY_Summary_{self.trsc_type}', filetypes=csv_files, defaultextension=csv_files)
		if not fd is None:
			self.custom_frames["create_treeview"].data.to_csv(fd, index=False)
		else:
			print("Recieved None!!")

	def on_close(self):
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules?")
			if cnf:
				self.child_tabs[0].on_cancel()
			else:
				return
		self.root.destroy()

	def toogle_fy(self):
		fy_id = self.current_fy.get()
		#print(self.trsc_type, fy_id)
		curr_data = get_trsc_data(self.trsc_type, fy_id)
		self.custom_frames["create_treeview"].data = curr_data
		self.custom_frames["create_treeview"].refill_table()
		#print(f"Loaded fy = {fy_id}")
		self.root.update()

	def _on_tab_close(self, title):
		self.parent._on_tab_close(title)
		self.child_tabs = []
		self.toogle_fy()

def SaleSummaryView(root, db_conn, title):
	return SummaryView(root, "sale", db_conn, title)

def PurchaseSummaryView(root, db_conn, title):
	return SummaryView(root, "purc", db_conn, title)

if __name__=="__main__":
	base = tk.Tk()
	base.notebook = ttk.Notebook(base)
	base.notebook.pack(expand=True, fill="both")
	sum_view = SummaryView(base, "sale", db_conn, "Sale Summary View")
	sum_view.build()
	base.mainloop()
