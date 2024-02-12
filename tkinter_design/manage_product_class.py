#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import Font_tuple
from menubar import menubar
from entries import entries
from commands import manage_prod
from combo_search import combosearch
from view_dataframe import create_treeview

## This code is somewhat horribly written! Please bear with it while debugging!
## It is yet to be debugged...

## Entries are not disabled at start. Why?
## The get_index() function is to be modified to perform few more tasks as suggested below
## Rest of the "manage_product_class" is to be modified accordingly 

class manage_product_class:
	def __init__(self,frame,prod_path,stock_path,**kwargs):
		self.frame = frame
		self.prod_path = prod_path
		self.stock_path = stock_path
		self.prod_class = manage_prod(prod_path,stock_path)
		for key,value in kwargs.items():
			setattr(self,key,value)
		if not hasattr(self,'font'):
			self.font = Font_tuple
	
	#def make_frame(self):
		self.heading = tk.Label(self.frame,text='Product Manager',font = head_font, fg='blue')
		self.heading.grid(row=0,column=0,columnspan=2,sticky=tk.W,padx=10,pady=10)

		self.v1 = tk.StringVar(self.frame,'ID00')
		#self.party_list = pd.read_csv(self.df_path)
		self.b1 = tk.Radiobutton(self.frame, text='Search by id', variable=self.v1, value='ID00', command=self.fill_labels)
		self.b1.grid(row=1,column=0)
		self.b2 = tk.Radiobutton(self.frame, text='Search by name', variable=self.v1, value='PRODUCT0', command=self.fill_labels)
		self.b2.grid(row=1,column=1)

		self.ss1 = combosearch(self.frame,plist = self.prod_class.prod_df[self.v1.get()].tolist(), ro=2,col=0, selectwhat=self.v1.get()[0] + self.v1.get()[1:-2].lower())
		self.ss1.labelize()

		self.ee1 = entries(self.frame,hlist = list(self.prod_class.prod_df.columns), ro=6,col=0)
		self.ee1.labelize()
		self.ee1.disable_entries()

		self.index = None
		
		self.ss1.b1.config(text='Load Selection', command = self.reload_data, font=Font_tuple)
		self.ss1.namechoosen.bind("<Return>",lambda event:self.reload_data)
		
		self.b_new = tk.Button(self.frame, text='Reload List',command=self.reload_main_list,font=self.font)
		self.b_new.grid(column=self.ss1.col+2,row=self.ss1.ro - 2,sticky=tk.W,padx=10,pady=3)
		
		self.bn = tk.Button(self.frame, text='Add New',command=self.add_new, font=self.font)
		self.bn.grid(row=6,column=2,padx=10,sticky=tk.W)

		self.be = tk.Button(self.frame, text='Edit Mode',command=self.edit_data, font=self.font)
		self.be.grid(row=7,column=2,padx=10,pady=3,sticky=tk.W)

		self.bs = tk.Button(self.frame, text='Save', command=self.to_save, font=self.font)
		self.bs.grid(row=8,column=2,padx=10,pady=3,sticky=tk.W)

		self.lw = tk.Label(self.frame,text='',fg='red')
		self.lw.grid(row=9,column=2,padx=10,pady=3,sticky=tk.W)


	def fill_labels(self):
		self.ss1.e1.delete(0,tk.END)
		self.ss1.plist = self.prod_class.prod_df[self.v1.get()].tolist()
		self.ss1.selectwhat = self.v1.get()[0] + self.v1.get()[1:-1].lower()
		self.ss1.reload_data(relabel=True)
	
	def reload_main_list(self):
		self.prod_class.reload()
		self.ss1.plist = self.prod_class.prod_df[self.v1.get()].tolist()

	def get_index(self,df,alias):		# Modify as suggested in "edit_data()" function
		plist = df['ID00'].tolist()
		if alias in plist:
			return plist.index(alias)
		else:
			return None

	def reload_data(self):
		self.ss1.getparty()
		self.ee1.enable_entries()
		self.ee1.elist = self.prod_class.prod_df[self.prod_class.prod_df[self.v1.get()] == self.ss1.out].iloc[0].tolist()
		self.ee1.relabel()
		self.ee1.disable_entries()
		self.index = int(self.get_index(self.prod_class.prod_df,self.ee1.elist[0]))
		
	def to_save(self):
		index = getattr(self,'index')
		new_var = self.ee1.get_entries()
		self.ee1.disable_entries()
		if index!=None:
			new_var.remove(new_var[0])
			new_var = [self.prod_class.prod_df,int(index)] + new_var
			self.prod_class.editex(*new_var)
			self.prod_class.save()
		else:
			if new_var[0] in self.prod_class.prod_df['ID00'].tolist():
				print("Cannot make new product, ID00 exists")
				self.lw.config(text="Cannot make new product,\n ID exists",font=self.font)
				self.ee1.enable_entries()
			else:	
				#new_var = [self.prod_class.prod_df] + new_var; >> Why did I write that?
				print(new_var)
				self.prod_class.addnew(*new_var)
				self.prod_class.save()
				print('New Product added', self.ee1.get_dict())
				
	def add_new(self):
		self.ee1.enable_entries()
		self.ee1.clear_entries()
		self.index = None

	def edit_data(self):
		self.ee1.enable_entries()
		self.ee1.ent0.config(state='disabled')
		#self.index = self.get_index() 
		'''Modify get_index() to get index without arguments and also take care of the radiobutton select'''


if __name__=='__main__':
	window = tk.Tk()
	window.title('Configure Party List')
	upper_menu = menubar(window,filename='manage_product_class.py')
	
	prod_path = '../scripts/sample_database/product_list.csv'
	stock_path = '../scripts/sample_database/product_stock.csv'
	
	prod_class = manage_product_class(window,prod_path,stock_path,font=Font_tuple)
	
	window.mainloop()
