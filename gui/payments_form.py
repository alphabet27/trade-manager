from ui_builder import *
from tkinter import messagebox

class PaymentsForm(UIBuilder):
	def __init__(self, parent, trsc_type, db_conn, title, mode='add', data=None, **kw):
		self.parent = parent
		root = ttk.Frame(parent.notebook)
		super().__init__(root, layout_file="layouts/payments_form.json")
		self.layout["title"] = title
		self.mode = mode
		self.db_conn = db_conn
		self.trsc_type = trsc_type
		if trsc_type=='purc':
			query_ptr = self.layout["custom_frames"]["party_select"]["sql_query"]
			query_ptr = query_ptr.replace('sale', 'purc')
		self.build(mode, data)

	def build(self, mode='add', data=None):
		super().build()
		if not data is None:
			for key, val in {"party_select":"ALIAS", "fy_select":"FY_ID"}.items():
				self.custom_frames[key].current_key.set(val)
				self.custom_frames[key].search_box.set(data.pop(val))
			print(f"Editing payment - New data = {data}")
		self.widgets["mode_label"].config(font=head_font)
		form_ptr = self.custom_frames["entry_block"]
		if not mode=='add':
			form_ptr.entry_dict.update(data)
		form_ptr.labelize()
		form_ptr.relabel()

	def on_save(self):
		data = {"FY_ID":"", "ALIAS":""}
		for key, val in {"fy_select":"FY_ID", "party_select":"ALIAS"}.items():
			self.custom_frames[key].get_data()
			data[val] = self.custom_frames[key].output[val]
			if data[val] is None:
				messagebox.showerror("Error", f"Please select {val}")
		table_name = f"{self.trsc_type}_payments_{data['FY_ID']}"
		pay_data = self.custom_frames["entry_block"].get_data()
		pay_data["ALIAS"] = data["ALIAS"]
		if pay_data["PAY_ID"]=="":
			del pay_data["PAY_ID"]
		cur = self.db_conn.cursor()
		sqlb.insert_row(cur, table_name, pay_data)
		self.db_conn.commit()
		self.on_cancel()

	def on_cancel(self):
		self.root.destroy()

def SalePaymentForm(parent, db_conn, title, **kw):
	return PaymentsForm(parent, 'sale', db_conn, title, **kw)

def PurchasePaymentForm(parent, db_conn, title, **kw):
	return PaymentsForm(parent, 'purc', db_conn, title, **kw)

