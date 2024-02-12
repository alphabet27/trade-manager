#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import Font_tuple
from menubar import menubar

## Subject to change -- Some functions that allow deleting and modifying treeview columns

def add_product(id00,product0,hsn=0,unit='na',gst=0):
	list0 = [id00,product0,hsn,unit,str(gst)+'%']
	prod_list.loc[len(prod_list)] = list0
	prod_list.to_csv('sample_database/product_list.csv',delimiter=',')

class create_treeview:
	def __init__(self,window,data,data2=None,ro=0,col=0,rospan=1,colspan=4,out='',scrollbar=None,font=Font_tuple):
		self.ro = ro
		self.col = col
		self.data = data
		self.font = Font_tuple
		self.data2 = data2
		self.window = window
		self.rospan = rospan
		self.colspan = colspan
		self.selection = None
		self.scrollbar = scrollbar
		
	def delete_treeview(self):
		if hasattr(self,'treeview'):
			for item in self.treeview.get_children():
				self.treeview.delete(item)
			self.treeview['show'] = 'headings'
			self.treeview.grid_forget()
			if hasattr(self,'l1'):
				self.l1.config(text='')
			if hasattr(self,'verscrlbar'):
				self.verscrlbar.grid_forget()
		else:
			print('No data found to clear!')
	
	def get_current_item(self):
		if hasattr(self,'treeview'):
			curItem = self.treeview.focus()
			self.selection = self.treeview.item(curItem)['values']
			print('Current selection -',self.selection)
			printable = '['
			for i in range(len(self.selection)-1):
				printable += str(self.selection[i]) + ', '
			if len(self.selection)>1:
				printable += str(self.selection[-1]) + ']'
			self.l1 = tk.Label(self.window,text=printable,font=self.font)
			self.l1.grid(row=self.ro+2,column=self.col,columnspan=self.colspan,sticky=tk.W)
			#print(dir(self.verscrlbar))
		else:
			print('No data to show!')


	def create_table(self,datlist):
		# Create a Treeview widget
		self.delete_treeview()
		self.treeview = ttk.Treeview(self.window) #, columns=prod_list.columns, show='headings')
		self.treeview.grid(row=self.ro,column=self.col,rowspan = self.rospan,columnspan=self.colspan, sticky='nsew')
		#self.scrollframe = tk.Frame(self.window)
		#self.verscrlbar.pack(fill='y')
		#self.scrollframe.grid(row=self.ro,column=self.col+self.colspan+1,sticky=tk.W)
		if type(self.scrollbar)==type(None):
			self.verscrlbar = ttk.Scrollbar(self.window,orient='vertical',command=self.treeview.yview)#,width=20)
			self.verscrlbar.grid(row=self.ro,column=self.col+self.colspan+1,rowspan=1,sticky='nsw')
			self.treeview.configure(xscrollcommand = self.verscrlbar.set)
		else:
			self.treeview.configure(xscrollcommand = self.scrollbar.set)
		self.treeview['show'] = 'headings'
		self.treeview['columns'] = list(datlist)
		style = ttk.Style()
		style.configure("Treeview", font=self.font)
		style.configure("Treeview.Heading", font=self.font)
		#tk.Grid.rowconfigure(self.window,self.ro,weight=1)		# This method did not work
		self.window.grid_rowconfigure(self.ro,weight=1)
		#self.window.grid_columnconfigure(self.col,weight=1)		# Nor did this :(
		#self.window.grid_columnconfigure(self.col + self.colspan + 1,weight=1)

		for name0 in list(datlist.columns):
			self.treeview.heading(name0, text=name0)
			self.treeview.column(name0, width=20*len(name0))  # Adjust the width as needed
			
		for index, row in datlist.iterrows():
		    self.treeview.insert('', 'end', values=row.tolist())
		    
		self.ro+=2

		#tab.treeview.bind("<ButtonRelease-1>", lambda self:print('Column is clicked \u25b2'))
			
	def add_buttons(self,b1_label='Product \nList'):
		self.b1 = tk.Button(self.window,text=b1_label,command=lambda:self.create_table(self.data),font=self.font)
		self.b1.grid(row=self.ro-1,column=self.col)
		self.b2 = tk.Button(self.window,text="Clear \nTable",command=self.delete_treeview,font=self.font)
		self.b2.grid(row=self.ro-1,column=self.col+1)
		if type(self.data2)!=type(None):
			self.b3 = tk.Button(self.window,text="Party \nList",command=lambda:self.create_table(self.data2),
			font=self.font)
			self.b3.grid(row=self.ro-1,column=self.col+2)
		self.b4 = tk.Button(self.window,text="Print \nCurrent \u25bc",command=self.get_current_item, font=self.font)
		self.b4.grid(row=self.ro-1,column=self.col+3)
		
		#start after 2 rows and 4 columns (or 'colspan' number of columns)
		

if __name__ == "__main__":
	prod_list = pd.read_csv('../scripts/sample_database/product_list.csv')
	party_list = pd.read_csv('../scripts/sample_database/party_list.csv')
	
	window = tk.Tk()
	window.title('Product List')
	
	menubar(window,filename='view_dataframe.py')

	tab = create_treeview(window,prod_list,data2=party_list)
	tab.add_buttons()

	# Start the Tkinter event loop
	window.mainloop()

