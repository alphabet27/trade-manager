#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from numpy import nan
from font import head_font
from font import Font_tuple
from entries import entries
from menubar import menubar
from commands import manage_prod
from commands import transactions
from tkcalendar import Calendar
from combo_search import combosearch, multi_selector
from view_dataframe import create_treeview

prod_map = '../scripts/sample_database/product_list.csv'
party_path = '../scripts/sample_database/party_list.csv'
stock_path = '../scripts/sample_database/product_stock.csv'
billdata_path = '../scripts/sample_database/sale_billdata.csv'
transactions_path = '../scripts/sample_database/sale_fulldata.csv'

''' 
	Make and test edit product functions.
	
	Figure out how to add/subtract stock on every transaction. 

	Why modifier_window.mainloop() starts before execution? Is it accidentally called somewhere.
	
	Anyways, atleast define self.root() along with base class and just keep mainloop and entry filling for popup.
	
'''

class transact_frame:
	def __init__(self,window,tr_manager,prod_manager,billno,addnew=False,**kwargs):
		self.index = None
		self.addnew = addnew
		self.window = window
		self.billno = billno				# Use 0 for new bill
		self.tr_manager = tr_manager
		self.prod_manager = prod_manager
		#self.modifier_window = modifier_window
		
		for key,value in kwargs.items():
			setattr(self,key,value)
		
		for key,value in {'ro':0, 
						  'col':0, 
						  'mode':'add',
						  'font':Font_tuple}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
		
		#self.date_picker = date_picker() --- to be defined
		
		self.bill_label = tk.Label(text = 'Showing bill : ',font=self.font)
		self.bill_label.grid(row=self.ro, column=self.col, sticky=tk.E)
		
		self.billno_label = tk.Label(text = str(self.billno),font=self.font)
		self.billno_label.grid(row=self.ro, column=self.col + 1, sticky=tk.W)
		self.ro+=1
		
		self.tr_manager.billdata(self.billno)
		
		self.ss1 = multi_selector(self.window,self.tr_manager.party_map,ro=self.ro,col=self.col)
		self.ss1.set_default(self.tr_manager.curr_billdata)
		
		self.ro += 6
		
		self.tab = create_treeview(self.window,self.tr_manager.df_bill, ro = self.ro, col = self.col)
		self.tab.create_table(self.tab.data)
		self.ro+=2
		
		self.add_prod = tk.Button(self.window, text = 'Add New', command = lambda:self.pop_up_window(), font = self.font)
		self.add_prod.grid(row = self.ro, column = self.col + 2, padx = 10, sticky = 'ew')
		
		self.edit_prod = tk.Button(self.window, text = 'Edit', command = lambda:self.pop_up_window(), font = self.font)
		self.edit_prod.grid(row=self.ro, column = self.col + 3, padx = 10, sticky = 'ew')
		
		self.ro+=1
		
		self.save_button = tk.Button(self.window, text='Save Bill', command=self.to_save, font=self.font)
		self.save_button.grid(row=self.ro, column=2, padx=10, pady=3, sticky='ew')
		
		self.close_button = tk.Button(self.window, text='Exit', command=lambda:self.window.destroy(), font=self.font)
		self.close_button.grid(row=self.ro, column=3, padx=10, pady=3, sticky='ew')
		
	def edit(self,prod_dict):
		#self.tr_manager.df_bill
		return None
		
	def append(self):
		if not self.addmode:
			self.tr_manager.df_bill.drop(list((self.tr_manager.df_bill['REF_NO']==self.curr_ref).index)[0])
		nb = max(self.tr_manager.df_bill.index) + 1
		temp = self.ee1.get_dict()
		temp['ID00'] = self.ss2.out['ID00']
		temp['PRODUCT0'] = self.ss2.out['PRODUCT0']
		temp['REF_NO'] = self.tr_manager.df_bill['REF_NO'].max() + 1
		temp['BATCH00'] = self.temp_stock[1]
		temp['EXP00'] = self.temp_stock[2]
		self.temp_stock[0] = temp['QTY']
		new_stock_iter = self.prod_manager.stock_data[temp['ID00']].subtract_stock(self.temp_stock)
		self.tr_manager.df_bill.loc[nb] = temp
		self.prod_manager.stock_data[temp['ID00']].update(new_stock_iter)
		self.prod_manager.update_stock(temp['ID00'])
		self.tab.create_table(self.tr_manager.df_bill)
		#print('Current billdata : \n',self.tr_manager.df_bill.head())
		print('New Product Entry : ',temp)
		self.root.destroy()
		
	def edit_prod(self):
		print('Yet to be defined')
		
	def to_save(self):
		print('')

	def pop_up_window(self,addmode=True,curr_ref=None):
		self.addmode=addmode
		if not addmode:
			self.curr_ref = curr_ref
			elist = self.tr_manager.df_bill[self.tr_manager.df_bill['REF NO']==curr_ref][['QTY','RATE']].to_list()
			
		self.root = tk.Tk()
		self.root.title('Add Product')
		
		self.ss2 = multi_selector(self.root, self.prod_manager.prod_df[['ID00','PRODUCT0']])
		if not addmode:
			self.ss2.set_default()

		inc = 5
		
		self.ee1 = entries(self.root, hlist = list(self.tr_manager.df_bill.iloc[0].to_dict().keys())[2:4],
						 ro = inc + 1, col = self.col)
		self.ee1.labelize()
		self.ee1.make_numeric(0)
		self.ee1.make_numeric(1,allowfloat=True)
		self.ee1.disable_entries()
		
		inc+=2
		
		self.batch_lab = ttk.Label(self.root, text='Select Batch : ', font=self.font)
		self.batch_lab.grid(row=inc+3, column = self.col, sticky=tk.E, padx = 9)
		
		self.batch_sel = ttk.Combobox(self.root, font=self.font, state='readonly')
		self.batch_sel.grid(row=inc+3, column = self.col + 1, sticky=tk.W, padx = 9)
		
		self.exp_label1 = ttk.Label(self.root, text = 'Expiry Date : ', font = self.font)
		self.exp_label2 = ttk.Label(self.root, text = '', font = self.font)
		
		self.exp_label1.grid(row = inc+4, column = 0, padx = 9, sticky = tk.E)
		self.exp_label2.grid(row = inc+4, column = 1, padx = 9, sticky = tk.W)
		
		def super_select():
			self.ss2.get_output()
			try:
				self.prod_manager.get_stock(self.ss2.out['ID00'])
				my_batlist = self.prod_manager.stock_data[self.ss2.out['ID00']]
				self.batch_sel['values'] = my_batlist.batches()
			except IndexError:
				self.batch_sel['values'] = ('None',)
				
		def exp_loader():
			exp = self.prod_manager.stock_data[self.ss2.out['ID00']].fetch_batch(self.batch_sel['values'][self.batch_sel.current()])
			self.temp_stock = exp
			self.exp_label2.config(text=exp[2])
			self.bal_label2.config(text=str(exp[0]))
		
		self.ss2.ss1.b1.config(command=super_select)
		self.ss2.ss1.namechoosen.bind('<Return>',lambda event:super_select())
		self.batch_sel.bind("<Return>", lambda event:exp_loader())
		
		self.bal_label1 = ttk.Label(self.root, text = 'Bal Stock : ', font = self.font)
		self.bal_label2 = ttk.Label(self.root, text = '', font = self.font)
		
		self.bal_label1.grid(row = inc+5, column = 0, padx = 9, sticky = tk.E)
		self.bal_label2.grid(row = inc+5, column = 1, padx = 9, sticky = tk.W)
		
		self.bs = tk.Button(self.root, text='Save', command=lambda:self.append(), font=self.font)
		self.bs.grid(row = inc + 4, column = 2, padx = 10, pady = 3, sticky = tk.W)
		
		if not addmode:
			self.bs.config(command=lambda:self.edit_prod())
		
		self.bx = tk.Button(self.root, text='Exit', command=lambda:self.confirm_exit(self.root), font=self.font)
		self.bx.grid(row = inc + 5, column = 2, padx = 10, pady = 3, sticky = tk.W)
		
		#self.root.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit(self.root))
		self.root.mainloop()
		
	def confirm_exit(self,what,mytext='Close without saving?'):
		def destroyer(conf,what):
			try:
				what.destroy()
				conf.destroy()
			except:
				conf.destroy()
		conf = tk.Tk()
		conf.title('Exit?')
		warn_label = tk.Label(conf,text=mytext)
		warn_label.grid(row=0,column=0,sticky='ew',columnspan=2,padx=10,pady=10)
		yes_button = tk.Button(conf,text='Yes',command=lambda:destroyer(conf,what),font=self.font)
		yes_button.grid(row=1,column=0,sticky='ew')
		no_button = tk.Button(conf,text='No',command=conf.destroy,font=self.font)
		no_button.grid(row=1,column=1,sticky='ew')
		conf.mainloop()

		
if __name__=='__main__':
	window = tk.Tk()
	window.title('Add/Edit Transactions')
	menubar(window,filename='transaction_make.py')
	
	tr_manager = transactions(party_path,billdata_path,transactions_path)
	prod_manager = manage_prod(prod_path = prod_map, stock_path = stock_path)
	
	transact_frame(window, tr_manager, prod_manager, billno=3)

	window.mainloop()
