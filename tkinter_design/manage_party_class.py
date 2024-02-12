#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from font import head_font
from font import Font_tuple
from menubar import menubar
from entries import entries
#from commands import editex, addnew
from commands import manage_party
from combo_search import combosearch
from view_dataframe import create_treeview

db_path = '../scripts/sample_database/party_list.csv'

class manage_party_class:
	def __init__(self,window,db_path,**kwargs):
		self.window = window
		#self.party_list = party_list
		self.db_path = db_path
		self.party_class = manage_party(db_path)
		for key,value in kwargs.items():
			setattr(self,key,value)
		if not hasattr(self,'font'):
			self.font = Font_tuple
		
		self.heading = tk.Label(self.window,text='Party Manager',font = head_font,fg='blue')
		self.heading.grid(row=0,column=0,columnspan=2,sticky=tk.W,padx=10,pady=10)

		self.v1 = tk.StringVar(self.window,'ALIAS00')

		self.b1 = tk.Radiobutton(self.window, text='Search by alias', variable=self.v1, value='ALIAS00', command=self.fill_labels,font=self.font)
		self.b1.grid(row=1,column=0)
		self.b2 = tk.Radiobutton(self.window, text='Search by party', variable=self.v1, value='PARTY00', command=self.fill_labels,font=self.font)
		self.b2.grid(row=1,column=1)

		self.ss1 = combosearch(self.window,plist = self.party_class.df_party[self.v1.get()].tolist(), ro=2,col=0, selectwhat=self.v1.get()[0] + self.v1.get()[1:-2].lower())
		self.ss1.labelize()

		self.ee1 = entries(self.window, hlist = list(self.party_class.df_party), elist = ['' for _ in self.party_class.df_party], ro=6, col=0)
		self.ee1.labelize()
		self.ee1.disable_entries()

		self.index = None
		
		self.ss1.b1.config(text='Load Selection',command=self.reload_data,font=self.font)
		self.ss1.namechoosen.bind("<Return>",lambda event:self.reload_data)
		
		self.b_new = tk.Button(text='Reload List',command=self.reload_main_list,font=self.font)
		self.b_new.grid(column=self.ss1.col+2,row=self.ss1.ro+2,sticky=tk.W,padx=10,pady=3)

		self.bn = tk.Button(self.window, text='Add New',command=self.add_new,font=self.font)
		self.bn.grid(row=6,column=2,padx=10,sticky=tk.W)

		self.be = tk.Button(self.window, text='Edit Mode',command=self.edit_data,font=self.font)
		self.be.grid(row=7,column=2,padx=10,sticky=tk.W)

		self.bs = tk.Button(self.window, text='Save',command=self.to_save,font=self.font)
		self.bs.grid(row=8,column=2,padx=10,sticky=tk.W)

		self.lw = tk.Label(self.window,text='',fg='red')
		self.lw.grid(row=9,column=2,padx=10,sticky=tk.W)
	
	def fill_labels(self):
		self.ss1.e1.delete(0,tk.END)
		self.ss1.plist = self.party_class.df_party[self.v1.get()].tolist()
		self.ss1.selectwhat = self.v1.get()[0] + self.v1.get()[1:-2].lower()
		self.ss1.reload_data(relabel=True)
		
	def get_index(self,df,alias):
		plist = df['ALIAS00'].tolist()
		if alias in plist:
			return plist.index(alias)
		else:
			return None

	def reload_data(self):
		self.ss1.getparty()
		self.ee1.enable_entries()
		self.ee1.elist = self.party_class.df_party[self.party_class.df_party[self.v1.get()] == self.ss1.out].iloc[0].tolist()
		self.ee1.relabel()
		self.ee1.disable_entries()
		self.index = int(self.get_index(self.party_class.df_party,self.ee1.elist[0]))
		
	def to_save(self): #,ee1,party_list):
		index = self.index
		new_var = self.ee1.get_entries()
		if index!=None:
			new_var.remove(new_var[0])
			new_var = [int(index)] + new_var
			self.party_class.editex(*new_var)
			self.party_class.save()
			self.ee1.disable_entries()
		else:
			if new_var[0] in self.party_class.df_party['ALIAS00'].tolist():
				print("Cannot make new party, alias exists")
				self.lw.config(text="Cannot make new party,\n alias exists",font=self.font)
			elif not new_var[4] in ['sale','purc']:
				self.lw.config(text="Unrecognized party type\nMust be 'sale' or 'purc\nPlease check spaces too'")
			else:	
				#new_var = [party_list] + new_var
				self.party_class.addnew(*new_var)
				self.party_class.save()
				self.ee1.disable_entries()
				
	def reload_main_list(self):
		self.party_class.reload()
		self.ss1.plist = self.party_class.df_party[self.v1.get()].tolist()
				
	def add_new(self):
		self.ee1.enable_entries()
		self.ee1.clear_entries()
		self.index = None

	def edit_data(self):
		self.ee1.enable_entries()
		self.ee1.ent0.config(state='disabled')


if __name__ == '__main__':
	window = tk.Tk()
	window.title('Configure Party List')
	
	menubar(window,'manage_party_class.py')
	party_window = manage_party_class(window,db_path,font=Font_tuple)

	window.mainloop()
