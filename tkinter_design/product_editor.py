import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import main_font
#from menubar import menubar
from entries_2 import entries
from commands import manage_prod
from sub_windows import exit_conf
from combo_search_2 import dual_selector

from tkinter.messagebox import showerror

# Bug													#	Priority
# Modify all functions to handle stock appropriately		V.High
# Test edits made to "mode==edit" option in "to_save"		Unknown

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

class product_class:
	def __init__(self,tab_name,notebook,database,attr_main={},**kwargs):
		self.tab_name = tab_name
		self.notebook = notebook
		self.attr_main = attr_main
		self.prod_class = manage_prod(database)
		
		self.frame = ttk.Frame(self.notebook)

		for key,value in kwargs.items():
			setattr(self,key,value)
			
		for key,value in {'ro':0, 
						  'col':0, 
						  'mode':'Idle',
						  'font':main_font,
						  'head_font':head_font}.items():
			if not hasattr(self,key):
				setattr(self,key,value)

		if not self.tab_name in self.attr_main.keys():
			self.make_frame()
			self.notebook.add(self.frame, text='INVENTORY MANAGER')
		else:
			print('Frame exists!')

	def make_frame(self):
		self.frame = ttk.Frame(self.notebook)
		self.heading = tk.Label(self.frame,text='Product Manager',font = self.head_font, fg='blue')
		self.heading.grid(row=self.ro, column=self.col, columnspan=2, sticky=tk.W, padx=10, pady=10)
		self.ro+=1
		
		self.ss1 = dual_selector(self.frame, self.prod_class.prod_df, ro = self.ro, col=self.col, addnone=True)
		self.ss1.ss1.b1.config(text = 'Load Current', command=self.load_selection)
		self.ss1.ss1.namechoosen.bind('<Return>',self.load_selection)
		self.ro+=6
		
		self.mode_label = tk.Label(self.frame, text = ' Add  Mode', font = self.head_font)
		self.mode_label.grid(row=self.ro, column=self.col, padx=10, pady=10)
		
		self.ro+=1
		
		cols = list(self.prod_class.prod_df.columns)
		cols.remove("STOCK")

		self.ee1 = entries(self.frame, edict = dict(zip(cols,['']*len(cols))), ro=self.ro, col=self.col)
		self.ee1.make_numeric(4,allowfloat=True,warnfunc=lambda acctype:self.lw.config(text=acctype+' values only'))
		self.ee1.disable_entries()

		#self.batch_sel = tk.ComboBox(self.frame)
		#self.ee2 = entries(self.frame, edict={'BATCH':'','QTY':''})
		
		self.addn_button = tk.Button(self.frame, text=' Add New', font=self.font, command=self.addn_mode)
		self.edit_button = tk.Button(self.frame, text='  Edit  ', font=self.font, command=self.edit_mode)
		self.delt_button = tk.Button(self.frame, text=' Delete ', font=self.font, command=self.delt_mode)
		
		self.addn_button.grid(row = self.ro+0, column = self.col+2, sticky='ew', padx=10)
		self.edit_button.grid(row = self.ro+1, column = self.col+2, sticky='ew', padx=10)
		self.delt_button.grid(row = self.ro+2, column = self.col+2, sticky='ew', padx=10)
		
		self.lw = tk.Label(self.frame, text='', fg='red', font=self.font)
		self.lw.grid(row = self.ro + 3, column = self.col + 2)
		
		self.ro+= len(self.ee1.edict)
		
		self.save_button = tk.Button(self.frame, text=' Save ', font=self.font, command=self.to_save)
		self.canc_button = tk.Button(self.frame, text='Cancel', font=self.font, command=lambda:exit_conf(self.frame))
		
		self.save_button.grid(row = self.ro, column = self.col + 2, sticky='ew', pady=10)
		self.canc_button.grid(row = self.ro, column = self.col + 3, sticky='ew', pady=10, ipadx=20)

		self.notebook.add(self.frame, text='Product Manager')
		
	def load_selection(self,event=None,*args):
		self.ee1.enable_entries()
		self.ss1.get_output()
		#self.ss1.out['GST'] = self.ss1.out['GST'][:-1]
		temp = {}
		temp.update(self.ss1.out)
		_ = temp.pop('STOCK')
		self.ee1.edict = temp
		self.ee1.relabel()
		self.ee1.disable_entries()
		self.mode_label.config(text = 'Idle  Mode ')
		self.mode = 'idle'
		
	def addn_mode(self):
		self.save_button.config(text=' Save ')
		self.ee1.enable_entries()
		self.ee1.clear_entries()
		self.mode = 'add'
		self.mode_label.config(text = ' Add  Mode ')
		
	def edit_mode(self):
		self.load_selection()
		self.save_button.config(text=' Save ')
		self.ee1.enable_entries()
		self.ee1.ent0.config(state='disabled')
		self.mode = 'edit'
		self.mode_label.config(text = ' Edit Mode ')
		
	def delt_mode(self):
		self.save_button.config(text='Delete')
		self.ee1.disable_entries()
		self.mode = 'delt'
		self.mode_label.config(text = ' Del. Mode')
		
	def to_save(self):
		new_var = self.ee1.get_entries()
		print(new_var)
		if self.mode == 'add':
			try:
				self.prod_class.addnew_dict(new_var)
				self.lw.config(text='Saved '+new_var['ID00']+'\nsuccessfully')
				self.prod_class.save()
				self.ee1.disable_entries()
			except KeyError:
				self.lw.config(text=" Cannot make new product,\n No Product ID")
			except IOError:
				self.lw.config(text=" Cannot make new product,\n Product ID exists")
		elif self.mode == 'edit':
			try:
				self.prod_class.editex(new_var)
				self.prod_class.save()
				self.ee1.disable_entries()
			except:
				self.lw.config(text=" Product Entry not found")
		elif self.mode == 'delt':
			#self.prod_class.drop()
			self.prod_class.save()
			self.ee1.disable_entries()
			self.lw.config(text="Delete not defined yet")
		else:
			self.lw.config(text="Idle Mode Active",font=self.font)
			
		
if __name__=='__main__':
	window = tk.Tk()
	window.title('Configure Product List')

	tabControl = ttk.Notebook(window)
	tabControl.pack(fill=tk.BOTH, expand=True)

	prod_class = product_class('inv_man',tabControl,database)
	
	window.report_callback_exception = lambda exc=None, val=None, tb=None : showerror('Error',message=str(val))
	window.mainloop()
