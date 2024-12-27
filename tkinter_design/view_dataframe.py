import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import main_font
#from menubar import menubar

class create_treeview:
	def __init__(self,window,data,ro=0,col=0,rospan=1,colspan=4,out='',scrollbar=None,font=main_font):
		self.ro = ro
		self.col = col
		self.data = data
		self.font = font
		self.window = window
		self.rospan = rospan
		self.colspan = colspan
		self.selection = None
		self.scrollbar = scrollbar
		self.sort_order = None

		self.ascending = tk.BooleanVar()
		self.ascending.set(True)
		self.create_table()
		self.add_buttons()

		self.l1 = tk.Label(self.window,text='',font=self.font)
		self.l1.grid(row=self.ro+2,column=self.col,columnspan=self.colspan,sticky=tk.W)
		
	def delete_treeview(self):
		if hasattr(self,'treeview'):
			for item in self.treeview.get_children():
				self.treeview.delete(item)
			self.treeview['show'] = 'headings'
			self.treeview.grid_forget()
			self.selection = None
			#if hasattr(self,'l1'):
			self.l1.config(text='')
			#if hasattr(self,'verscrlbar'):
			self.verscrlbar.grid_forget()
		#else:
		#print('No data found to clear!')
	
	def get_current_item(self):
		#if hasattr(self,'treeview'):
		curItem = self.treeview.focus()
		self.selection = self.treeview.item(curItem)['values']
		print('Current selection -',self.selection)
		print('Type currsel',type(self.selection))
		printable = str(self.selection)
		if not self.selection is None:
			self.l1.config(text=printable)
		else:
			pass


	def create_table(self,datlist=None):
		print('Reloading table')
		if datlist is None:
			datlist=self.data
		self.delete_treeview()
		self.treeview = ttk.Treeview(self.window) #, columns=prod_list.columns, show='headings')
		self.treeview.grid(row=self.ro,column=self.col,rowspan = self.rospan,columnspan=self.colspan, sticky='nsew')
		if self.scrollbar is None:
			self.verscrlbar = ttk.Scrollbar(self.window,orient='vertical',command=self.treeview.yview)#,width=20)
			self.verscrlbar.grid(row=self.ro,column=self.col+self.colspan+1,rowspan=1,sticky='ns')	#'nsw'
			self.treeview.configure(xscrollcommand = self.verscrlbar.set)
		else:
			self.treeview.configure(xscrollcommand = self.scrollbar.set)
		self.treeview['show'] = 'headings'
		self.treeview['columns'] = list(datlist)
		style = ttk.Style()
		style.configure("Treeview", font=self.font)
		style.configure("Treeview.Heading", font=self.font)
		self.window.grid_rowconfigure(self.ro,weight=1)
		for i in range(self.colspan):
			self.window.grid_columnconfigure(self.col+i,weight=1)
		for name0 in list(datlist.columns):
			self.treeview.heading(name0, text=name0)
			self.treeview.column(name0, width=20*len(str(name0)))  # Adjust the width as needed
			
		for index, row in datlist.iterrows():
		    self.treeview.insert('', 'end', values=row.tolist())

		self.treeview.bind('<Button-3>', lambda event:self.right_click_menu(event))
		    

	def add_buttons(self,b1_label='Reload Table'):
		self.b1 = tk.Button(self.window,text=b1_label,command=lambda:self.create_table(self.data),font=self.font)
		self.b1.grid(row=self.ro+self.rospan, column=self.col, sticky='ew')
		self.b2 = tk.Button(self.window, text="Clear Table", command=self.delete_treeview, font=self.font)
		self.b2.grid(row=self.ro+self.rospan, column=self.col+1, sticky='ew')
		self.b4 = tk.Button(self.window,text="Print Current \u25bc", command=self.get_current_item, font=self.font)
		self.b4.grid(row=self.ro+self.rospan, column=self.col+self.colspan-1, sticky='ew')
		
		#start after 2 rows and 4 columns (or 'colspan' number of columns)
		
	def right_click_menu(self, event):
		self.M = tk.Menu(tearoff=0)
		self.MS = tk.Menu(self.M,tearoff=0)
		print(list(self.treeview['columns']))
		for column in list(self.treeview['columns']):
			setattr(self,'MS_'+column,self.MS.add_command(label = column, command=lambda my_col=column :self.sort_by_column(my_col)))
		self.MS.add_separator()
		self.MS.add_radiobutton(label='Ascending', variable=self.ascending, value=True, command=lambda my_col=column :self.sort_by_column())
		self.MS.add_radiobutton(label='Descending', variable=self.ascending, value=False, command=lambda my_col=column :self.sort_by_column())
		
		self.MS.add_separator()
		self.MS.add_command(label='Multi Sort', command=self.multi_sort)
		
		self.M.add_cascade(label='Reload', command=self.create_table)
		self.M.add_cascade(label='Sort by :', menu=self.MS)
		self.M.post(event.x_root, event.y_root)
		
	def sort_by_column(self, column=None):
		if column is None:
			if self.sort_order is None:
				column = self.data.columns[0]
			else:
				column = self.sort_order[0]
		print('Sorting by',column)
		print('Sorting by percentage values may give unexpected results')
		self.data = self.data.sort_values(column, axis=0, ascending=self.ascending.get())
		self.sort_order = [column]
		self.create_table(self.data)
		
	def multi_sort(self):
		self.sort_win = tk.Tk()
		cols = list(self.treeview['columns'])
		sort_ord = []
		for i in range(len(cols)):
			setattr(self,'s'+str(i),tk.Checkbutton(self.sort_win,text=cols[i], command = lambda j=i: mod_order(j)))
			getattr(self,'s'+str(i)).grid(row=i,column=0,sticky='w')
		def mod_order(j):
			if cols[j] in sort_ord:
				sort_ord.remove(cols[j])
			else:
				sort_ord.append(cols[j])
			self.so_lab.config(text=str(sort_ord))
		self.so_lab = tk.Label(self.sort_win,text=str(sort_ord))
		self.so_lab.grid(row=0,column=1,sticky='w')
		self.go_sort = tk.Button(self.sort_win, text='Sort',command=lambda:self.sort_by_column(sort_ord))
		self.go_sort.grid(row=1,column=1,sticky='e')
		self.sort_win.mainloop()
		self.sort_order = sort_ord

if __name__ == "__main__":
	prod_list = pd.read_csv('../scripts/sample_database/product_list.csv')
	party_list = pd.read_csv('../scripts/sample_database/party_list.csv')
	
	window = tk.Tk()
	window.title('Product List')
	
	#mm = menubar(window,filename='view_dataframe.py')

	tab = create_treeview(window,prod_list)

	tab.treeview.bind('<Button-3>', lambda event:tab.right_click_menu(event))

	window.mainloop()

