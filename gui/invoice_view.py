from ui_builder import *

db_conn = sqlb.get_connection()

class InvoiceView(UIBuilder):
	def __init__(self, parent, trsc_type, fy_id, billdata, *args, db_conn = db_conn, add_mode=False, view_mode=False, **kwargs):
		table_name = f"{trsc_type}_billdata_{fy_id}"
		self.fy_id = fy_id
		self.parent = parent
		self.db_conn = db_conn
		self.billdata = billdata
		self.trsc_type = trsc_type
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/individual_view.json")
		if add_mode:
			self.layout["custom_frames"]["widget_block"]["disabled"] = []
			del self.layout["custom_frames"]["create_treeview"]["params"]
		else:
			self.layout["custom_frames"]["create_treeview"]["from_sql"] = True
			self.layout["custom_frames"]["create_treeview"]["params"] = (billdata["BILL"],)
			self.layout["custom_frames"]["create_treeview"]["sql"] = sqlb.get_transactions_query(self.trsc_type, self.fy_id)
		if view_mode:
			frame_ptr = self.layout["frames"]
			for widget in frame_ptr["controls_1"]["widgets"]:
				widget["state"] = "disabled"
			for widget in frame_ptr["controls_2"]["widgets"]:
				if widget["text"] in ["Save"]:
					widget["state"] = "disabled"
		self.build()
		alias = billdata.pop("ALIAS")
		self.custom_frames["search_block"].current_key.set("ALIAS")
		self.custom_frames["search_block"].search_box.set(alias)
		self.custom_frames["widget_block"].entry_dict.update(billdata)
		print(self.custom_frames["widget_block"].entry_dict)
		self.custom_frames["widget_block"].labelize()
		self.custom_frames["widget_block"].relabel()
		self.child_tabs = []
		#
		if view_mode:
			self.custom_frames["widget_block"].disable_entries(disable_all=True)
			self.custom_frames["search_block"].mode_button.config(state="disabled")

	def add_tab(self, title, trsc_data, **kw):
		if not "BILL" in self.custom_frames["widget_block"].disabled:
			self.custom_frames["widget_block"].disabled.append("BILL")
			self.custom_frames["widget_block"].relabel()
		if len(self.child_tabs)!=0:
			raise Exception("Found open Sub-Modules!")
			return
		self.parent._open_tab("TransactionForm", title = title, billdata = self.billdata, trsc_type = self.trsc_type, fy_id = self.fy_id, trsc_data = trsc_data, no_bind=True, **kw)
		self.child_tabs.append(self.parent.tab_instances[title])
		self.child_tabs[0].root.bind("<Destroy>", lambda e, t=title: self._on_tab_close(t))

	def _on_tab_close(self, title):
		self.parent._on_tab_close(title)
		self.child_tabs = []
		self.on_refresh()

	def on_add(self):
		tr_cols = list(self.custom_frames["create_treeview"].data.columns)
		tr_data = dict(zip(tr_cols, [""]*len(tr_cols)))
		del tr_data["TAXABLE"], tr_data["PRODUCT_NAME"], tr_data["HSN_CODE"]
		tr_data["BILL"] = self.billdata["BILL"]
		if len(self.custom_frames["create_treeview"].data)>0:
			tr_data["SR_NO"] = int(self.custom_frames["create_treeview"].data["SR_NO"].max() + 1)
		else:
			tr_data["SR_NO"] = 1
		print(f"Opening Transaction {tr_data}")
		self.add_tab("Add Trsc", tr_data, add_mode=True)

	def on_edit(self):
		tr_data = self.custom_frames["create_treeview"].get_current(search_by=["SR_NO"])
		del tr_data["TAXABLE"], tr_data["PRODUCT_NAME"], tr_data["HSN_CODE"]
		print(f"Opening Transaction {tr_data}")
		self.add_tab("Edit Trsc", tr_data)

	def on_delete(self):
		print("Delete")

	def on_refresh(self):
		self.custom_frames["create_treeview"].refill_table(reload_data=True)

	def on_save(self):
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules?")
			if cnf:
				self.child_tabs[0].on_cancel()
			else:
				return
		self.parent.db_conn.commit()
		self.root.destroy()

	def on_print(self):
		print("Print")

	def on_exit(self):
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules?")
			if cnf:
				self.child_tabs[0].on_cancel()
			else:
				return
		self.parent.db_conn.rollback()
		self.root.destroy()

if __name__=="__main__":
	root = tk.Tk()
	root.notebook = ttk.Notebook(root)
	root.notebook.pack(expand=True, fill="both")
	inv = InvoiceView(root, "sale", "fy_25", {"BILL":1, "ALIAS":"alias04", "INVOICE_DATE":"05/08/2024"})
	inv.root.pack(expand=True, fill="both")
	root.mainloop()
