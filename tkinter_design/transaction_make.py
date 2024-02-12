#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import Font_tuple
from entries import entries
from menubar import menubar
from commands import manage_prod
from commands import transactions
#from commands import multi_transact
from tkcalendar import Calendar
from combo_search import combosearch
from view_dataframe import create_treeview
#from secondary_windows import confirm_exit

prod_map = '../scripts/sample_database/product_list.csv'
party_path = '../scripts/sample_database/party_list.csv'
stock_path = '../scripts/sample_database/product_stock.csv'
billdata_path = '../scripts/sample_database/sale_billdata.csv'
transactions_path = '../scripts/sample_database/sale_data.csv'

''' Try adding a "class pop_up_window" instead of a function, maybe that serves better '''

class transact_frame:
	def __init__(self,window,tr_manager,prod_manager,addnew=False,**kwargs):
		self.index = None
		self.addnew = addnew
		self.window = window
		#self.billno = 'new_bill'
		self.tr_manager = tr_manager
		self.prod_manager = prod_manager
		
		for key,value in kwargs.items():
			setattr(self,key,value)
		
		for key,value in {'ro':0, 'col':0, 'mode':'add','font':Font_tuple}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
		
		#self.date_picker = date_picker() --- to be defined
		self.bill_label = tk.Label(text = 'Showing bill no : ',font=self.font)
		self.bill_label.grid(row=self.ro, column=self.col, sticky=tk.E)
		self.ro+=1
		
		self.ss1 = combosearch(self.window,
							plist=pd.read_csv(self.tr_manager.party_path,usecols=['PARTY00'])['PARTY00'].to_list(),
							ro = self.ro + 1, col = self.col)
		self.ss1.labelize()
		
		self.tab = create_treeview(self.window,self.tr_manager.billdata(2),
									ro = self.ss1.ro + 1, col = self.col)
		self.tab.add_buttons(b1_label='Show\nTransactions')
		self.tab.b3 = tk.Button(self.window, text='Add\nNew',command=lambda:self.pop_up_window(), font=self.font)
		self.tab.b3.grid(row = self.ss1.ro, column = self.col + 2, padx = 10, sticky = tk.W)
		
		
		self.sepstyle = ttk.Style()
		self.sepstyle.configure('blue.TSeparator', background='blue')
		self.sep = ttk.Separator(self.window, orient=tk.HORIZONTAL, takefocus=0).grid(row=self.ss1.ro + 6, column=0, columnspan=3)
		
		self.save_button = tk.Button(self.window, text='Save Bill', command=self.to_save, font=self.font)
		self.save_button.grid(row=self.ss1.ro + 7,column=3,padx=10,pady=3,sticky=tk.W)
		
	def add_new(self):
		self.ee1.enable_entries()
		self.ee1.clear_entries()
		self.index = None

	def edit_data(self):
		self.ee1.enable_entries()
		self.ee1.ent0.config(state='disabled')
		
	def append(self):
		nb = max(self.tr_manager.df_bill.index) + 1
		temp = self.ee1.get_dict()
		temp['ID00'] = self.ss2.out
		temp['REF_NO'] = self.tr_manager.df_bill['REF_NO'].max() + 1
		#temp['BATCH00'] = self.batch_sel.selection() - Make a line to add batch number
		#temp['EXP00'] = self.batch_sel.selection()
		self.tr_manager.df_bill.loc[nb] = temp
		self.tab.create_table(self.tr_manager.df_bill)
		print('Current billdata : \n',self.tr_manager.df_bill.head())
		print('New Product Entry : ',temp)
		self.root.destroy()
		
	def edit_prod(self):
		print('Yet to be defined')
		
	def pop_up_window(self,mode='add',elist=None):
		self.root = tk.Tk()
		self.root.title('Add Product')
		self.ss2 = combosearch(self.root, plist=self.prod_manager.prod_df['ID00'].to_list(),
					ro = 0, col = 0, selectwhat='Product')
		self.ss2.labelize()
		inc = 3
		
		self.ee1 = entries(self.root, hlist=list(self.tr_manager.df_bill.iloc[0].to_dict().keys())[2:4],
						 ro = inc + 1, col = self.col)
		self.ee1.labelize()
		self.ee1.make_numeric(0)
		self.ee1.make_numeric(1)
		self.ee1.disable_entries()
		
		self.batch_lab = ttk.Label(self.root, text='Select Batch : ', font=self.font)
		self.batch_lab.grid(row=inc+3, column = self.col, sticky=tk.E, padx = 9)
		
		self.batch_sel = ttk.Combobox(self.root, font=self.font, state='readonly')
		self.batch_sel.grid(row=inc+3, column = self.col + 1, sticky=tk.W, padx = 9)
		
		self.exp_label1 = ttk.Label(self.root, text = 'Expiry Date : ', font = self.font)
		self.exp_label2 = ttk.Label(self.root, text = '', font = self.font)
		
		self.exp_label1.grid(row = inc+4, column = 0, padx = 9, sticky = tk.E)
		self.exp_label2.grid(row = inc+4, column = 1, padx = 9, sticky = tk.W)
			
		self.bs = tk.Button(self.root, text='Save', command=lambda:self.append(), font=self.font)
		self.bs.grid(row = inc + 3, column = 2, padx = 10, pady = 3, sticky = tk.W)
		
		if mode=='edit':
			self.bs.config(command=lambda:self.edit_prod())
		
		self.bx = tk.Button(self.root, text='Exit', command=lambda:self.confirm_exit(self.root), font=self.font)
		self.bx.grid(row = inc + 4, column = 2, padx = 10, pady = 3, sticky = tk.W)
		
		self.root.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit(self.root))
		self.root.mainloop()
		
	def confirm_exit(self,what,mytext='Close without saving?'):
		def destroyer(conf,what):
			what.destroy()
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
	
	def to_save(self):
		print('')
		#self.tr_manager()
		
if __name__=='__main__':
	window = tk.Tk()
	window.title('Add/Edit Transactions')
	menubar(window,filename='transaction_make.py')
	
	tr_manager = transactions(party_path,billdata_path,transactions_path)
	prod_manager = manage_prod(prod_path = prod_map, stock_path = stock_path)
	
	transact_frame(window, tr_manager, prod_manager)

	window.mainloop()
