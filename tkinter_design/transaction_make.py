import json
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import *
from entries_2 import entries
from commands import manage_prod
from commands import manage_party
from commands import transactions
from commands import make_document
from tkcalendar import Calendar
from combo_search_2 import dual_selector #, combosearch
from transaction_product_entry import pop_up_window
from view_dataframe import create_treeview
import tkinter.messagebox as messagebox
from sub_windows import exit_conf, billno_window, error_message

# Bug															Severity
# Define stock manager for arbitrary closure					High
# For new bill (billno=0) >>>
#	why is product column being displayed at right corner??		Done
# Resolve conflict of variables in multiple instances			Done (There was no conflict. A label
#																without window was created)

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}


class transact_frame:
	def __init__(self,window,tr_manager,billno=0,**kwargs):
		self.window = window
		self.billno = billno		# Use 0 for new bill
		self.subdata = {'DATE0':'', 'CHL. No.':'', 'CHL. Dt.':'','P.O. No.':'', 'P.O. Dt.':''}
		self.database = database
		self.tr_manager = tr_manager
		self.prod_manager = manage_prod(database)
		#self.party_manager = party_manager

		for key,value in kwargs.items():
			setattr(self,key,value)

		for key,value in {'ro':0,
						  'col':0,
						  #'mode':'add',
						  'font':main_font,
						  'head_font':head_font}.items():
			if not hasattr(self,key):
				setattr(self,key,value)

		#self.date_picker = date_picker() --- to be defined

		self.bill_label = tk.Label(self.window ,text = 'Showing bill : ' + str(self.billno),font=self.head_font)
		self.bill_label.grid(row=self.ro, column=self.col, columnspan=2, sticky='w')

		self.ro+=1

		self.tr_manager.billdata(self.billno)
		ds_default = {}

		if not self.tr_manager.curr_billdata is None:
			ds_default['ALIAS0'] = self.tr_manager.curr_billdata.pop('ALIAS0')
			temp = self.tr_manager.get_party_data(ds_default['ALIAS0']) #,get_full=True)
			ds_default.update(temp)
		else:
			ds_default = None

		self.ss1 = dual_selector(self.window, self.tr_manager.party_map, default = ds_default, ro=self.ro, col=self.col)

		if not self.billno==0:
			self.subdata.update(json.loads(self.tr_manager.curr_billdata['SUBDATA']))
			self.subdata['DATE0'] = self.tr_manager.curr_billdata['DATE0']

		self.ee1 = entries(self.window, edict = self.subdata, ro=self.ro, col=self.col+3)
		self.ee1.relabel()
		#self.ee1.disable_entries()

		self.ro += 7

		self.tab = create_treeview(self.window,self.tr_manager.df_bill, ro = self.ro, col = self.col, colspan=6)
		self.ro+=2

		self.add_prod = tk.Button(self.window, text = 'Add New', command = lambda:self.pop_up_window(editmode=False), font = self.font)
		self.add_prod.grid(row = self.ro - 1, column = self.col + 4, sticky = 'ew')

		self.edit_prod = tk.Button(self.window, text = 'Edit', command = lambda:self.pop_up_window(editmode=True), font = self.font)
		self.edit_prod.grid(row=self.ro, column = self.col + 4, sticky = 'ew')

		self.print_button = tk.Button(self.window, text = 'Print Bill', command = lambda:self.print_bill(), font=self.font)
		self.print_button.grid(row=self.ro, column = self.col + 5, sticky = 'ew')

		self.ro+=1

		self.save_button = tk.Button(self.window, text='Save Bill', command=self.to_save, font=self.font)
		self.save_button.grid(row=self.ro, column=4, pady=3, sticky='ew')

		self.close_button = tk.Button(self.window, text='Exit', command=self.confirm_exit, font=self.font)
		self.close_button.grid(row=self.ro, column=5, pady=3, sticky='ew')

	def pop_up_window(self,editmode=False):
		self.tab.get_current_item()
		if editmode and (not self.tab.selection == ''):
			ent_dict = dict(zip(self.tab.treeview["columns"],self.tab.selection))
			print(ent_dict)
		elif editmode and self.tab.selection == '':
			editmode = False
			ent_dict = {}
			self.tab.l1.config(text='No item selected \nOpening in ADD MODE')
		else:
			ent_dict = {}
		self.pp1 = pop_up_window(self.window,self.prod_manager, self.tr_manager, editmode=editmode, ent_dict=ent_dict)
		self.pp1.launch()
		print('Pop up window is now closed')
		print('Closed pop_up_window with save status',self.pp1.save_succ)
		self.tab.create_table()
		print('Created table at popup close')
		if ((not self.pp1.save_succ) and editmode):
			self.pp1.sh1.decrease(ent_dict['BATCH00'],ent_dict['QTY'])
			self.prod_manager.update_stock(self.pp1.sh1)
			print('Saving failed, restored stock to',self.pp1.sh1.stock_info)

	def to_save(self):
		self.ss1.get_output()
		curr_billdata = {}
		#curr_billdata.update(self.tr_manager.curr_billdata)
		curr_billdata.update(self.ss1.out)
		self.subdata = self.ee1.get_entries()
		for key,value in self.subdata.items():
			if value=='':
				_ = self.subdata.pop(key)
			else:
				pass
		curr_billdata['DATE0'] = self.subdata.pop('DATE0')
		curr_billdata.update({'SUBDATA':json.dumps(self.subdata)})
		print('Saving bill. Passing following data to transactions class')
		for key,value in curr_billdata.items():
			print(key.rjust(16),':\t',value)
		if self.billno == 0:
			self.bb1 = billno_window(self.window, billno_default=self.tr_manager)
			print('Recieved billno',self.bb1.value.get())
			self.tr_manager.add_transactions(self.bb1.value.get(),curr_billdata)
		else:
			self.tr_manager.edit_transactions(billdata=curr_billdata)
		self.tr_manager.save()
		self.prod_manager.save()
		self.window.destroy()

	def confirm_exit(self,mytext='Close without saving?'):
		cf_1 = exit_conf(self.window)

	def print_bill(self):
		self.ss1.get_output()
		invoice_info = {}
		invoice_info.update({"customer_info":self.tr_manager.get_party_data(self.ss1.out['ALIAS0'], get_full=True)})
		invoice_info.update(self.ee1.get_entries())
		invoice_info.update({"bill_df_ren":self.tr_manager.df_bill})
		print('Recieved the following invoice_info')
		for key, value in invoice_info.items():
			print(key.ljust(16),':\t',value)
		print('To be continued...')

if __name__=="__main__":
	window = tk.Tk()
	window.title('Test Window')
	prod_manager = manage_prod(database)
	tr_manager = transactions(database)
	tr_frame = transact_frame(window,tr_manager,billno=3)
	window.mainloop()
