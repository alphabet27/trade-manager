#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import Font_tuple
from entries import entries
from menubar import menubar
from commands import manage_prod
from combo_search import combosearch, multi_selector

# Test edits made to "mode==edit" option in "to_save"

class new_product_class:
	def __init__(self,frame,prod_path,stock_path,**kwargs):
		self.frame = frame
		self.prod_path = prod_path
		self.stock_path = stock_path
		self.prod_class = manage_prod(prod_path,stock_path)
		
		for key,value in kwargs.items():
			setattr(self,key,value)
			
		for key,value in {'ro':0, 
						  'col':0, 
						  'mode':'Idle',
						  'font':Font_tuple,
						  'head_font':head_font}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
			
		self.heading = tk.Label(self.frame,text='Product Manager',font = self.head_font, fg='blue')
		self.heading.grid(row=self.ro, column=self.col, columnspan=2, sticky=tk.W, padx=10, pady=10)
		self.ro+=1
		
		self.ss1 = multi_selector(self.frame, self.prod_class.prod_df, ro = self.ro, col=self.col, addnone=True)
		self.ss1.ss1.b1.config(text = 'Load Current', command=self.load_selection)
		self.ss1.ss1.namechoosen.bind('<Return>',self.load_selection)
		self.ro+=5
		
		self.mode_label = tk.Label(self.frame, text = ' Add  Mode', font = self.head_font)
		self.mode_label.grid(row=self.ro, column=self.col, padx=10, pady=10)
		
		self.ro+=1
		
		self.ee1 = entries(self.frame, hlist = list(self.prod_class.prod_df.columns), ro=self.ro, col=self.col)
		self.ee1.labelize()
		self.ee1.disable_entries()
		
		self.addn_button = tk.Button(self.frame, text=' Add New', font=self.font, command=self.addn_mode)
		self.edit_button = tk.Button(self.frame, text='  Edit  ', font=self.font, command=self.edit_mode)
		self.delt_button = tk.Button(self.frame, text=' Delete ', font=self.font, command=self.delt_mode)
		
		self.addn_button.grid(row = self.ro+0, column = self.col+2, sticky='w', padx=10)
		self.edit_button.grid(row = self.ro+1, column = self.col+2, sticky='w', padx=10)
		self.delt_button.grid(row = self.ro+2, column = self.col+2, sticky='w', padx=10)
		
		self.lw = tk.Label(self.frame, text='', fg='red', font=self.font)
		self.lw.grid(row = self.ro + 3, column = self.col + 2)
		
		self.ro+= len(self.ee1.hlist)
		
		self.save_button = tk.Button(self.frame, text=' Save ', font=self.font, command=self.to_save)
		self.canc_button = tk.Button(self.frame, text='Cancel', font=self.font)
		
		self.save_button.grid(row = self.ro, column = self.col + 1, sticky='se', pady=10)
		self.canc_button.grid(row = self.ro, column = self.col + 2, sticky='sw', pady=10)
		
	def load_selection(self,event=None,*args):
		self.ee1.enable_entries()
		self.ss1.get_output()
		self.ee1.elist = list(self.ss1.out.values())
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
		new_var = self.ee1.get_dict()
		print(new_var)
		if self.mode == 'add':
			try:
				self.prod_class.addnew_dict(new_var)
				self.lw.config(text='Saved'+new_var['ID00']+'\nsuccessfully')
				self.prod_class.save()
				self.ee1.disable_entries()
			except KeyError:
				self.lw.config(text=" Cannot make new product,\n No Product ID")
			except IOError:
				self.lw.config(text=" Cannot make new product,\n Product ID exists")
		elif self.mode == 'edit':
			#ind = self.prod_class.get_index(new_var)
			#if ind:
				#del new_var['ID00']
				#self.prod_class.prod_df.loc[ind,new_var.keys()] = new_var.values()
			try:
				self.prod_class.editex(new_var)
				self.prod_class.save()
				self.ee1.disable_entries()
			#else:
			except:
				self.lw.config(text=" Product Entry not found")
		elif self.mode == 'delt':
			self.prod_class.drop()
			self.prod_class.save()
			self.ee1.disable_entries()
		else:
			self.lw.config(text="Idle Mode Active",font=self.font)
			
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
			
		
if __name__=='__main__':
	window = tk.Tk()
	window.title('Configure Product List')
	upper_menu = menubar(window,filename='product_latest.py')
	
	prod_path = '../scripts/sample_database/product_list.csv'
	stock_path = '../scripts/sample_database/product_stock.csv'
	
	prod_class = new_product_class(window,prod_path,stock_path,font=Font_tuple)
	
	window.mainloop()
