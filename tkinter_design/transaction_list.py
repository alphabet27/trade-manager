import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import head_font
from font import main_font
from commands import transactions
from transaction_make import transact_frame
from view_dataframe import create_treeview

# Open transactions from notebook instead of frame.

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

class transaction_frame:
	def __init__(self,tab_name,notebook,database,attr_main={},**kwargs):
		self.tab_name = tab_name
		self.notebook = notebook
		self.database = database
		self.attr_main = attr_main
		self.tr_manager = transactions(database)
		kw1 = {'ro':0,'col':0,'font':main_font,'sub_frames':[]}
		kw1.update(kwargs)
		for key,value in kw1.items():
			setattr(self,key,value)
		#self.year_sel = ttk.Combobox(self.frame)
		''' Add a financial year selector (combosearch) that will decide the transactions path
			This will help when sorting according to financial years. '''
		#
		if not self.tab_name in self.attr_main.keys():
			self.make_frame()
			self.notebook.add(self.frame, text='TRANSACTIONS MANAGER')
		else:
			print('Frame exists!')

	def make_frame(self):
		self.frame = ttk.Frame(self.notebook)
		self.main_label = tk.Label(self.frame,text='Transactions List', font=head_font)
		self.main_label.grid(row=0,column=0,sticky='n',padx=10)
		self.vline = ttk.Separator(self.frame, orient='vertical')
		self.vline.grid(row=self.ro,column=self.col+1,rowspan=4,padx=2,sticky='ns')

		self.col+=2

		self.tab = create_treeview(self.frame,self.tr_manager.full_data(),ro=self.ro, col=self.col,colspan=6)

		self.add_button = tk.Button(self.frame, text='Add New', font=self.font, command = lambda:self.make_edits())
		self.add_button.grid(row=self.ro+self.tab.rospan,column=self.tab.col+4,sticky='ew')

		self.edit_button = tk.Button(self.frame, text='Edit', font=self.font, command = lambda:self.make_edits(edit_trsc=True))
		self.edit_button.grid(row=self.tab.ro+self.tab.rospan+1,column=self.tab.col+4,sticky='ew')

		self.canc_button = tk.Button(self.frame, text='Exit', font=self.font)
		self.canc_button.grid(row=self.tab.ro+self.tab.rospan+1,column=self.tab.col+5,sticky='ew')

	def make_edits(self,edit_trsc=False,*args,**kwargs):
		if edit_trsc:
			self.tab.get_current_item()
			if self.tab.selection=='':
				billno = 0
				tab_name = 'add_mode'
				print('No bill selected. Switching to add mode!')
			else:
				billno = self.tab.selection[0]
				tab_name = 'edit_mode'
				label = 'EDIT MODE : ' + str(billno)
		else:
			billno = 0
			label = 'ADD MODE'
			tab_name = 'add_mode'
		self.tr_manager.billdata(billno)	# Pull data from here (Remove line in transaction_make)
		l = len(self.sub_frames)
		self.sub_frames.append('add_or_edit_trsc_'+str(l))
		setattr(self,'sub_frame'+str(l),ttk.Frame(self.notebook))
		self.attr_main['add_or_edit_trsc_'+str(l)]=transact_frame(getattr(self,'sub_frame'+str(l)), self.tr_manager, billno=billno, **kwargs)
		self.notebook.add(getattr(self,'sub_frame'+str(l)), text=label)
		self.notebook.select(getattr(self,'sub_frame'+str(l)))
		#self.notebook.pageconfigure('trsc_man', state='disabled')

	def save_edits(self):
		#self.tr_manager.add
		pass

	def disable_page(self):
		pass



if __name__=='__main__':
	window = tk.Tk()
	window.title('Add/Edit Transactions')
	window.state('zoomed')

	tabctrl = ttk.Notebook(window)
	tabctrl.pack(fill=tk.BOTH, expand=True)

	tr_frame = transaction_frame('trsc_man',tabctrl,database)
	
	window.mainloop()
