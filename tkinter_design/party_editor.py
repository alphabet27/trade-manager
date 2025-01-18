import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import main_font
#from menubar import menubar
from entries_2 import entries
from commands import manage_party
from sub_windows import exit_conf
from combo_search_2 import dual_selector

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

class party_class:
	def __init__(self,tab_name,notebook,database,attr_main={},**kwargs):
		self.tab_name = tab_name
		self.notebook = notebook
		self.attr_main = attr_main
		self.party_class = manage_party(database)
		
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
			self.notebook.add(self.frame, text='ACCOUNT MANAGER')
		else:
			print('Frame exists!')

	def make_frame(self):
		self.heading = tk.Label(self.frame,text='Party Manager',font = self.head_font, fg='blue')
		self.heading.grid(row=self.ro, column=self.col, columnspan=2, sticky=tk.W, padx=10, pady=10)
		self.ro+=1
		
		self.ss1 = dual_selector(self.frame, self.party_class.df_party, ro = self.ro, col=self.col, addnone=True)
		self.ss1.ss1.b1.config(text = 'Load Current', command=self.load_selection)
		self.ss1.ss1.namechoosen.bind('<Return>',self.load_selection)
		self.ro+=6
		
		self.mode_label = tk.Label(self.frame, text = ' Add  Mode', font = self.head_font)
		self.mode_label.grid(row=self.ro, column=self.col, padx=10, pady=10)
		
		self.ro+=1
		
		heads = list(self.party_class.df_party.columns)[:-1]

		self.ee1 = entries(self.frame, edict = dict(zip(heads,['']*len(heads))), ro=self.ro, col=self.col)
		self.ee1.make_numeric(3)
		self.ee1.disable_entries()
		
		self.ro+=len(self.ee1.edict)
		
		self.type_label = tk.Label(self.frame, text = 'Type :', font=self.font)
		self.type_select = ttk.Combobox(self.frame, font=self.font, state='readonly', values=['sale','purc'])
		
		self.type_label.grid(row=self.ro, column=self.col, sticky='e', padx=12)
		self.type_select.grid(row=self.ro, column=self.col+1, sticky='w', padx=8)
		
		self.ro-= len(self.ee1.edict)
		
		self.addn_button = tk.Button(self.frame, text=' Add New', font=self.font, command=self.addn_mode)
		self.edit_button = tk.Button(self.frame, text='  Edit  ', font=self.font, command=self.edit_mode)
		self.delt_button = tk.Button(self.frame, text=' Delete ', font=self.font, command=self.delt_mode)
		
		self.addn_button.grid(row = self.ro+0, column = self.col+2, sticky='w', padx=10)
		self.edit_button.grid(row = self.ro+1, column = self.col+2, sticky='w', padx=10)
		self.delt_button.grid(row = self.ro+2, column = self.col+2, sticky='w', padx=10)
		
		self.lw = tk.Label(self.frame, text='', fg='red', font=self.font)
		self.lw.grid(row = self.ro + 3, column = self.col + 2)
		
		self.ro+= len(self.ee1.edict)
		
		self.save_button = tk.Button(self.frame, text=' Save ', font=self.font, command=self.to_save)
		self.canc_button = tk.Button(self.frame, text='Cancel', font=self.font, command=lambda:exit_conf(self.frame))
		
		self.save_button.grid(row = self.ro + 1, column = self.col + 2, sticky='ew', pady=10)
		self.canc_button.grid(row = self.ro + 1, column = self.col + 3, sticky='ew', pady=10, ipadx=20)

		self.notebook.add(self.frame, text='Account Manager')
		
	def load_selection(self,event=None,*args):
		self.ee1.enable_entries()
		self.ss1.get_output()
		self.type_select.set(self.ss1.out['TYPE'])
		self.type_select.config(state='disabled')
		self.ss1.out.pop('TYPE')
		self.ee1.edict = self.ss1.out
		self.ee1.relabel()
		self.ee1.disable_entries()
		self.mode_label.config(text = 'Idle  Mode ')
		self.mode = 'idle'
		
	def addn_mode(self):
		self.save_button.config(text=' Save ')
		self.ee1.enable_entries()
		self.ee1.clear_entries()
		self.type_select.config(state='readonly')
		self.mode = 'add'
		self.mode_label.config(text = ' Add  Mode ')
		
	def edit_mode(self):
		self.load_selection()
		self.save_button.config(text=' Save ')
		self.ee1.enable_entries()
		self.ee1.ent0.config(state='disabled')
		self.type_select.config(state='readonly')
		self.mode = 'edit'
		self.mode_label.config(text = ' Edit Mode ')
		
	def delt_mode(self):
		self.save_button.config(text='Delete')
		self.ee1.disable_entries()
		self.type_select.config(state='disabled')
		self.mode = 'delt'
		self.mode_label.config(text = ' Del. Mode')
		
	def to_save(self):
		new_var = self.ee1.get_entries()
		new_var['TYPE'] = self.type_select.get()
		print(new_var)
		if self.mode == 'add':
			try:
				self.party_class.addnew_dict(new_var)
				self.lw.config(text='Saved '+new_var['ALIAS0']+' \nsuccessfully')
				self.party_class.save()
				self.ee1.disable_entries()
				self.type_select.config(state='disabled')
			except KeyError:
				self.lw.config(text=" Cannot make new party,\n No alias")
			except IOError:
				self.lw.config(text=" Cannot make new product,\n alias exists")
		elif self.mode == 'edit':
			self.party_class.edit_by_dict(new_var)
			self.party_class.save()
			self.ee1.disable_entries()
			self.type_select.config(state='disabled')
		elif self.mode == 'delt':
			temp_ser = self.party_class.df_party['ALIAS0']
			self.party_class.df_party.drop(temp_ser[temp_ser==self.ss1.out['ALIAS0']].index, inplace=True)
			self.party_class.save()
			self.ee1.disable_entries()
			self.type_select.config(state='disabled')
		else:
			self.lw.config(text="Idle Mode Active",font=self.font)

		
if __name__=='__main__':
	window = tk.Tk()
	window.title('Configure Party List')
	
	tabControl = ttk.Notebook(window)
	tabControl.pack(fill=tk.BOTH, expand=True)

	party_class = party_class(tabControl,database)
	
	window.mainloop()
