from ui_builder import *
import gen_report as rept
from tkinter import messagebox

db_conn = sqlb.get_connection()

def get_taxables(df):
	tax_list = df.GST.unique()
	taxables = {}
	for i, tax in enumerate(tax_list):
		sub_df = df[df.GST==tax]
		taxables[f"Taxable {tax:.2f}"] = (sub_df.QTY*sub_df.RATE*(1 - sub_df.DISC/100)).sum()
		taxables[f"Taxable {tax:.2f}"] = round(taxables[f"Taxable {tax:.2f}"], 2)
		taxables[f"Tax {tax:.2f}"] = taxables[f"Taxable {tax:.2f}"]*tax/100
		if i>4:
			messagebox.showerror("Info", "Too many taxes! Showing first 4")
			break
	return taxables

class InvoiceView(UIBuilder):
	def __init__(self, parent, trsc_type, fy_id, billdata, *args, db_conn = db_conn, add_mode=False, view_mode=False, **kwargs):
		table_name = f"{trsc_type}_billdata_{fy_id}"
		self.fy_id = fy_id
		self.parent = parent
		self.db_conn = db_conn
		self.add_mode = add_mode
		self.billdata = billdata
		self.trsc_type = trsc_type
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/individual_view.json")
		# if add_mode:
		# 	self.layout["custom_frames"]["widget_block"]["disabled"] = ["BILL"]
		# 	del self.layout["custom_frames"]["create_treeview"]["params"]
		# else:
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
		alias = billdata["ALIAS"]
		self.custom_frames["search_block"].current_key.set("ALIAS")
		self.custom_frames["search_block"].search_box.set(alias)
		self.custom_frames["widget_block"].entry_dict.update(billdata)
		del self.custom_frames["widget_block"].entry_dict["ALIAS"]
		print(self.custom_frames["widget_block"].entry_dict)
		for wb_name in ["widget_block", "info_block_1", "info_block_2"]:
			self.custom_frames[wb_name].labelize()
			self.custom_frames[wb_name].relabel()
		self.child_tabs = []
		#
		if view_mode:
			self.custom_frames["widget_block"].disable_entries(disable_all=True)
			self.custom_frames["search_block"].mode_button.config(state="disabled")
			self.on_refresh()

	def add_tab(self, title, trsc_data, **kw):
		self.db_conn.execute("SAVEPOINT trsc_form")
		self.custom_frames["search_block"].get_data()
		if self.custom_frames["search_block"].output is None:
			#self.db_conn.execute("RELEASE SAVEPOINT trsc_form")
			raise Exception("Please select a party!!")
			return
		self.billdata["ALIAS"] = self.custom_frames["search_block"].output["ALIAS"]
		if not "BILL" in self.custom_frames["widget_block"].disabled:
			billno = self.custom_frames["widget_block"].BILL_e.get()
			df = sqlb.SQL_DataFrame(con=self.db_conn, sql=f"SELECT * FROM {self.trsc_type}_billdata_{self.fy_id} WHERE BILL=?", params=(billno,))
			if len(df)>0 and self.trsc_type=="sale":
				#self.db_conn.execute("RELEASE SAVEPOINT trsc_form")
				raise Exception("Bill Number Exists!!")
				return
			self.custom_frames["widget_block"].disabled.append("BILL")
			self.custom_frames["widget_block"].relabel()
		if len(self.child_tabs)!=0:
			#self.db_conn.execute("RELEASE SAVEPOINT trsc_form")
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
		cnf = messagebox.askyesnocancel("Warning!", "Confirm Delete Action?")
		if cnf:
			cursor = self.db_conn.cursor()
			q = f"DELETE FROM {self.trsc_type}_fulldata_{self.fy_id} WHERE TID=?"
			tr_data = self.custom_frames["create_treeview"].get_current(search_by=["SR_NO"])
			stock_data = dict(PID = tr_data["PID"], QTY=tr_data["QTY"], BATCH=tr_data["BATCH"],
							  EXPIRY=tr_data["EXPIRY"], MRP=tr_data["MRP"])
			sqlb.increment_stock(self.db_conn, stock_data, self.trsc_type, pop_null=True)
			cursor.execute(q, (tr_data["TID"],))
			self.db_conn.commit()
			self.on_refresh()
		else:
			return

	def on_refresh(self):
		self.custom_frames["create_treeview"].refill_table(reload_data=True, use_con=self.db_conn)
		taxables = get_taxables(self.custom_frames["create_treeview"].data)
		info_ptr = self.custom_frames["info_block_1"]
		info_ptr.entry_dict = dict(taxables)
		info_ptr.disabled = list(taxables.keys())
		info_ptr.output = dict(taxables)
		self.custom_frames["info_block_2"].entry_dict.update({"Grand Total":sum(info_ptr.entry_dict.values())})
		for ptr in ["info_block_1", "info_block_2"]:
			self.custom_frames[ptr].labelize()
			self.custom_frames[ptr].relabel()

	def on_save(self, close_tab=True):
		cursor = self.db_conn.cursor()
		billdata = self.custom_frames["widget_block"].get_data()
		self.custom_frames["search_block"].get_data()
		alias = self.custom_frames["search_block"].output["ALIAS"]
		billdata.update({"ALIAS":alias})
		if self.add_mode:
			sqlb.insert_row(cursor, f"{self.trsc_type}_billdata_{self.fy_id}", billdata)
		else:
			sqlb.update_rows(cursor, f"{self.trsc_type}_billdata_{self.fy_id}", "BILL", billdata)
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules? (Data will not be saved!)")
			if cnf:
				self.child_tabs[0].on_cancel()
			else:
				return
		self.parent.db_conn.commit()
		if close_tab:
			self.root.destroy()
		else:
			self.db_conn.execute("SAVEPOINT invoice_modif")

	def on_print(self):
		self.on_save(False)
		sel_ptr = self.custom_frames["search_block"]
		table_ptr = self.custom_frames["create_treeview"]
		billdata = self.custom_frames["widget_block"].get_data()
		sel_ptr.get_data()
		print("Printing bill =",billdata)
		invoice_info = sqlb.get_invoice_data(self.db_conn, sel_ptr.output["ALIAS"], billdata)
		print("customer_info =", invoice_info["customer_info"])
		invoice_info["bill_df_ren"] = sqlb.pd.DataFrame(table_ptr.data)
		invoice_info["bill_df_ren"]["RATE"] = (invoice_info["bill_df_ren"]["RATE"]*(1 - invoice_info["bill_df_ren"]["DISC"]/100)).round(decimals=2)
		doc = rept.make_doc(rept.document_info, show_cols = rept.inv_cols)
		doc.make_header()
		footer_info = rept.get_footer(rept.document_info, invoice_info["bill_df_ren"])
		doc.make_invoice_table(invoice_info, footer_info, rept.inv_cols)
		doc.save(f'../reports/Invoice_{self.trsc_type}/{str(int(invoice_info["BILL"])).rjust(6, "0")}_{invoice_info["customer_info"]["ALIAS"]}',source=False,doc=True)

	def on_exit(self):
		if len(self.child_tabs)>0:
			cnf = messagebox.askyesnocancel("Warning!", "Close Sub-Modules?")
			if cnf:
				self.child_tabs[0].on_cancel()
				self.db_conn.execute("RELEASE SAVEPOINT invoice_modif")
				self.root.destroy()
			else:
				return
		else:
			self.db_conn.execute("RELEASE SAVEPOINT invoice_modif")
			self.root.destroy()

if __name__=="__main__":
	root = tk.Tk()
	root.geometry("1200x600")
	root.notebook = ttk.Notebook(root)
	root.notebook.pack(expand=True, fill="both")
	inv = InvoiceView(root, "sale", "fy_25", {"BILL":2, "ALIAS":"Sujay", "INVOICE_DATE":"05/08/2024"})
	inv.root.pack(expand=True, fill="both")
	root.mainloop()
