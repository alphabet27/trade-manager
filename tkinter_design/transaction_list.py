#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import Font_tuple
from entries import entries
from menubar import menubar
from commands import transactions
from combo_search import combosearch
from view_dataframe import create_treeview

#prod_map = '../scripts/sample_database/product_list.csv'

party_path = '../scripts/sample_database/party_list.csv'
billdata_path = '../scripts/sample_database/sale_billdata.csv'
transactions_path = '../scripts/sample_database/sale_fulldata.csv'

class transaction_frame:
	def __init__(self,window,tr_manager,**kwargs):		#transactions_path,
		self.window = window
		self.tr_manager = tr_manager
		
		for key,value in kwargs.items():
			setattr(self,key,value)
		if not hasattr(self,'ro'):
			self.ro = 0
		if not hasattr(self,'col'):
			self.col = 0
		
		#self.year_sel = ttk.Combobox(self.window)
		
		''' Add a financial year selector (combosearch) that will decide the transactions path
			This will help when sorting according to financial years. '''
		
		self.tab = create_treeview(self.window,self.tr_manager.full_data())
		self.tab.add_buttons(b1_label='Show\nTransactions')
		#tab.b1.config(command=lambda:modified_b1(tab))
		
		self.tab.b3 = tk.Button(self.window, text='Open\nTransaction', font=self.font)
		self.tab.b3.grid(row=self.tab.ro+1,column=self.tab.col+2)
		

if __name__=='__main__':
	window = tk.Tk()
	window.title('Add/Edit Transactions')
	menubar(window,filename='transaction_list.py')
	
	tr_manager = transactions(party_path,billdata_path,transactions_path)
	tr_frame = transaction_frame(window,tr_manager,font=Font_tuple)
	
	window.mainloop()
