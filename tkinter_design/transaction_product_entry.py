import pandas as pd
from tkinter import ttk
#from menubar import menubar
from commands import manage_prod
from commands import manage_party
from commands import transactions
from tkcalendar import Calendar
from combo_search_2 import combosearch, dual_selector
from view_dataframe import create_treeview
from sub_windows import *

# Pending task											  # Importance
# Handle stock subtraction in editmode						V. High
# Complete get_fulldata() function							V. High
# Pull database from database.json							Medm
# Use messagebox in tkinter to implement confirm_exit		Low
# Handle "load_stock" for cases when there is no batch		Done
# Something wrong with make_numeric in entries				Done

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

class pop_up_window:
	def __init__(self,base_win,prod_manager,tr_manager,editmode=False,ent_dict={}):
		self.base_win = base_win
		self.editmode = editmode
		self.ent_dict = ent_dict
		self.save_succ = False
		self.final_data = {}
		self.tr_manager = tr_manager
		self.prod_manager = prod_manager
		
		self.font = main_font
		self.ro = 0
		self.col = 0
		
		self.window = tk.Toplevel(self.base_win)
		self.window.grid_columnconfigure(0, minsize=170)
		self.window.grid_rowconfigure(0, minsize=40)

		self.ss1 = dual_selector(self.window, self.prod_manager.prod_df, ro=self.ro)
		
		print("Conflict test",self.prod_manager.prod_df is self.ss1.df)

		self.ro+=6

		self.ee1 = entries(self.window, edict = {'QTY':'','RATE':'','DISC':''}, ro=self.ro, col=0)
		self.ee1.lab2.config(text='DISC %')
		self.ee1.make_numeric(0)
		self.ee1.make_numeric(1,allowfloat=True)
		self.ee1.make_numeric(2,allowfloat=True)
		
		self.bh = tk.Button(self.window, text='Get History', font=self.font, command = lambda : self.show_history(None))
		self.bh.grid(row = self.ro+1, column=2, padx = 10, pady = 3, sticky = 'ew')
		
		self.ro+=3
		
		self.batch_lab = ttk.Label(self.window, text='Select Batch : ', font=self.font)
		self.batch_lab.grid(row=self.ro, column = 0, sticky=tk.E, padx = 8)

		self.quick_lab = tk.Button(self.window, text='Quick Add', font=self.font, command=self.quick_add)
		self.quick_lab.grid(row=self.ro+1, column = 2, sticky='ew', padx = 8)

		self.quick_ldr = tk.Button(self.window, text='Load Batch', font=self.font, command=self.load_stock)
		self.quick_ldr.grid(row=self.ro, column = 2, sticky='ew', padx = 8)
		
		self.batch_sel = ttk.Combobox(self.window, font=self.font, state='readonly')
		self.batch_sel.grid(row=self.ro, column = 1, sticky=tk.W, padx = 3, pady=7)
		
		self.ro+=1
		
		self.exp_label1 = ttk.Label(self.window, text = 'Expiry Date : ', font = self.font)
		self.exp_label2 = ttk.Label(self.window, text = '', font = self.font)
		
		self.exp_label1.grid(row = self.ro, column = 0, padx = 9, sticky = tk.E)
		self.exp_label2.grid(row = self.ro, column = 1, padx = 9, sticky = tk.W)
		
		self.ro+=1
		
		self.bal_label1 = ttk.Label(self.window, text = 'Bal Stock : ', font = self.font)
		self.bal_label2 = ttk.Label(self.window, text = '', font = self.font)

		self.bal_label1.grid(row = self.ro, column = 0, padx = 9, pady=10, sticky = tk.E)
		self.bal_label2.grid(row = self.ro, column = 1, padx = 9, pady=10, sticky = tk.W)
		
		self.bs = tk.Button(self.window, text='Save', command=self.get_fulldata, font=self.font)
		self.bs.grid(row = self.ro+1, column = 1, ipadx=30, pady = 3, sticky = tk.E)
		
		self.bx = tk.Button(self.window, text='Exit', command=lambda:self.confirm_exit(self.window), font=self.font)
		self.bx.grid(row = self.ro+1, column = 2, padx = 10, pady = 3, sticky = 'ew')
		
		
		if not self.editmode:
			self.window.title('Add Product')
		else:
			self.window.title('Edit Product')
			print(self.ent_dict)
			self.ss1.default = {'ID00':self.ent_dict['ID00'],
								'PRODUCT0':self.ent_dict['PRODUCT0']}
			self.ee1.edict = {'QTY':self.ent_dict['QTY'],
							  'RATE':self.ent_dict['RATE'],
							  'DISC':self.ent_dict['DISC']}
			print(self.ee1.edict)
			self.ee1.relabel()
			sd_old = {'BATCH':self.ent_dict['BATCH00'],
					  'EXP':self.ent_dict['EXP00'],
					  'QTY':self.ent_dict['QTY']}
			self.sh1 = self.prod_manager.get_stock(self.ent_dict['ID00'])
			self.sh1.update_dict(sd_old)
			self.prod_manager.update_stock(self.sh1)
			self.load_batch()
			self.batch_sel.set(self.ent_dict['BATCH00'])

		self.ee1.disable_entries()
		# Event Bindings
		self.ss1.ss1.namechoosen.bind('<Return>', lambda event:self.load_batch())
		self.ss1.ss1.b1.config(command=self.load_batch)
		self.batch_sel.bind('<Return>', lambda event:self.load_stock())
		#self.batch_sel.bind('<FocusOut>', lambda event:self.exp_loader())
		self.ss1.b3.config(text='Unfreeze Entry',command=self.mode_switch)

	def launch(self):
		self.window.transient(self.base_win)
		self.window.grab_set()
		self.base_win.wait_window(self.window)
		#print('The launch completed')

	def load_batch(self):
		self.ss1.get_output()
		#print('self.ss1.out =',self.ss1.out)
		self.sh1 = self.prod_manager.get_stock(self.ss1.out['ID00'])
		if self.sh1.stock_info == {}:
			if not self.editmode:
				self.sh1.update_dict({"BATCH":"","QTY":0,"EXP":""})
			else:
				self.sh1.update_dict({"BATCH":"","QTY":self.ent_dict['QTY'],"EXP":""})
		my_batlist = list(self.sh1.stock_info.keys())
		self.batch_sel['values'] = my_batlist
		self.batch_sel.set(my_batlist[0])

	def load_stock(self):
		curid = self.ss1.out
		if curid=={}:
			raise Exception('No product selected!!')
		else:
			curr_batch = self.sh1.stock_info[self.batch_sel.get()]
			self.exp_label2.config(text=curr_batch['EXP'])
			self.bal_label2.config(text=curr_batch['QTY'])

	def mode_switch(self):
		if self.ss1.editmode:
			self.ss1.mode_switch()
			self.ee1.disable_entries()
		else:
			self.ss1.mode_switch()
			self.ee1.enable_entries()

	def quick_add(self):
		self.load_stock()
		self.sh1 = self.prod_manager.get_stock(self.ss1.out['ID00'])
		self.qacl = quick_add_window(self.window)
		#self.qacl.qa_root.mainloop()
		print('The quick add window is now closed with save status',self.qacl.save_succ)
		if self.qacl.save_succ:
			self.sh2 = self.qacl.output
			self.sh1.update_dict(self.sh2)
			self.prod_manager.update_stock(self.sh1)
			self.load_batch()
		else:
			pass
		
	def confirm_exit(self,mytext='Close without saving?'):
		cf_1 = exit_conf(self.window)
		
	def show_history(self, tr_manager):
		win_history = tk.Tk()
		curr_prod = self.ss1.out
		if not curr_prod=={}:
			df = self.tr_manager.df_transaction[self.tr_manager.df_transaction['ID00']==curr_prod['ID00']]
			tt1 = create_treeview(win_history, df)
		else:
			warn_label = tk.Label(win_history,text='No data found to display')
			warn_label.grid(row=0,column=0)
		win_history.mainloop()
		win_history.quit()

	def get_fulldata(self):
		temp = {}
		temp.update(self.ss1.out)
		if temp=={}:
			raise Exception('No product selected')
		temp.update(self.ee1.get_entries())
		temp.update({'BATCH':self.batch_sel.get()})
		print(self.sh1.stock_info)
		temp.update({'EXP':self.sh1.stock_info[temp['BATCH']]['EXP']})
		l1 = self.tr_manager.df_bill.index.max() + 1
		temp['REF_NO'] = 1
		if len(self.tr_manager.df_bill)>0:
			temp['REF_NO'] = self.tr_manager.df_bill.REF_NO.max()+1
		if self.editmode:
			temp['REF_NO'] = self.ent_dict['REF_NO']
			l1 = self.tr_manager.df_bill[self.tr_manager.df_bill.REF_NO == temp['REF_NO']].index[0]
		self.sh1.decrease(temp['BATCH'],temp['QTY'])
		self.prod_manager.update_stock(self.sh1)
		print('pop_up_window returning',temp)
		print('Updated stock >>>')
		for key,value in self.sh1.stock_info.items():
			print('\t',key,':',value)
		temp['BATCH00'] = temp.pop('BATCH')
		temp['EXP00'] = temp.pop('EXP')
		temp['TAXABLE'] = temp['QTY']*temp['RATE']*(100 - temp['DISC'])/100
		self.tr_manager.df_bill.loc[l1] = temp
		self.final_data.update(temp)
		self.save_succ = True
		self.window.destroy()
		self.window.update()
		# self.window.quit()

if __name__=='__main__':
	prod_manager = manage_prod(prod_path = database['product_path'])
	tr_manager = transactions(database)
	base_win = tk.Tk()
	base_win.title('Test window')
	base_win.minsize(200,200)

	def launch_pop_up():
		my_win = pop_up_window(base_win,prod_manager, tr_manager, editmode=True, ent_dict={'REF_NO': 2, 'ID00': 'id04', 'PRODUCT0': 'sample04', 'QTY': 8, 'RATE': 200, 'DISC': '0.0', 'BATCH00': 'batch04', 'EXP00': 'exp04', 'TAXABLE': '400.0'})
		#my_win.mm = menubar(my_win.window, filename='transaction_product_entry.py')
		my_win.window.minsize(550,350)
		my_win.window.report_callback_exception = lambda exc=None, val=None, tb=None:error_message(exc,val,tb)
		my_win.launch()

	b1 = tk.Button(base_win,text='Launch',command=launch_pop_up)
	b1.grid(row=0,column=0,padx=40,pady=40,ipadx=20,ipady=20)
	base_win.report_callback_exception = lambda exc=None, val=None, tb=None:error_message(exc,val,tb)
	base_win.mainloop()
