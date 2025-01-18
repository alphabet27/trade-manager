import tkinter as tk
from commands import ledger_manager
from combosearch_2 import dual_selector
from view_dataframe import create_treeview

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}


class ledger_frame:
	def __init__(self,frame,tr_manager):
		self.frame = frame
		self.tr_manager = tr_manager
		self.ledger_manager = ledger_manager(database)

		for key,value in kwargs.items():
			setattr(self,key,value)

		for key,value in {'ro':0,
						  'col':0,
						  #'mode':'add',
						  'font':main_font,
						  'head_font':head_font}.items():
			if not hasattr(self,key):
				setattr(self,key,value)

		self.ss1 = dual_selector(self.frame, self.tr_manager.party_map, default = ds_default, ro=self.ro, col=self.col)
		self.tab = create_treeview(self.frame, self.tr_manager.df_bill, ro = self.ro, col = self.col, colspan=6)

		self.save_button = tk.Button(self.window, text='Save Bill', command=self.to_save, font=self.font)
		self.save_button.grid(row=self.ro, column=4, pady=3, sticky='ew')

		self.close_button = tk.Button(self.window, text='Exit', command=self.confirm_exit, font=self.font)
		self.close_button.grid(row=self.ro, column=5, pady=3, sticky='ew')

	def to_save(self):
		pass

	def confirm_exit(self):
		pass

if __name__=="__main__":
	pass

