import tkinter as tk
from tkinter import ttk
import sql_backend as sqlb
from font import *

class create_treeview(ttk.Treeview):
	SORT_ORDER = None
	def __init__(self, base_frame, *args, sql=None, show_only=None, widths=None, **kwargs):
		if not "con" in kwargs.keys():
			kwargs["con"] = sqlb.get_connection()
		self.sql = sql
		self.kwargs = kwargs
		self.data = sqlb.SQL_DataFrame(sql=sql, **kwargs)
		self.font = main_font
		self.widths = widths
		self.show_only = show_only
		self.top_frame = tk.Frame(base_frame)
		self.base_frame = base_frame
		self.right_click_options = {}

		super().__init__(self.top_frame)
		self['show'] = 'headings'
		self['columns'] = list(self.data.columns)

		if not show_only is None:
			self['columns'] = list(show_only)

		self.ASCENDING = tk.BooleanVar(value=True)

		if widths is None:
			self.widths = dict(zip(self['columns'], [100]*len(self['columns'])))

		for i, column in enumerate(self['columns']):
			self.heading(column, text=column, command=lambda event=None, col=column:self.sort_data(col))
			self.column(column, width=self.widths[column])

		self.refill_table()
		self.bind("<Button-3>", self.right_click_menu)

	def refill_table(self, reload_data=False, use_con=None):
		if reload_data:
			self.data = sqlb.SQL_DataFrame(sql=self.sql, **self.kwargs)
			if not use_con is None:
				self.kwargs["con"] = use_con
		self.clear_table()
		for i, row in self.data.iterrows():
			temp1 = row.to_dict()
			temp2 = []
			for col in self['columns']:
				temp2.append(temp1[col])
			self.insert('','end', values=temp2)

	def clear_table(self):
		self.delete(*self.get_children())
		self.base_frame.update()

	def grid(self, *args, **kwargs):
		col_widths = list(self.widths.values())
		super().grid(row=0, column=0, columnspan = len(col_widths), sticky='nsew')
		#
		self.xscroll_bar = tk.Scrollbar(self.top_frame, orient='horizontal', command=self.xview)
		self.yscroll_bar = tk.Scrollbar(self.top_frame, orient='vertical', command=self.yview)
		#
		self.config(xscrollcommand = self.xscroll_bar.set, yscrollcommand = self.yscroll_bar.set)
		#
		self.xscroll_bar.grid(row = 1, columnspan=len(col_widths), column=0, sticky='new')
		self.yscroll_bar.grid(row = 0, column=len(col_widths)+1, sticky='nsw')
		#
		self.top_frame.grid(*args, **kwargs)
		s = sum(col_widths)
		for col, width in enumerate(self.widths.values()):
			self.top_frame.columnconfigure(col, weight = width)
		self.top_frame.rowconfigure(0, weight=1)
		self.top_frame.rowconfigure(1, weight=0)
		self.base_frame.grid_rowconfigure(kwargs['row'], weight=1)
		self.base_frame.grid_columnconfigure(kwargs['column'], weight=1)

	def sort_data(self, columns):
		self.SORT_ORDER = columns
		if not self.SORT_ORDER is None:
			self.data.sort_values(columns, ascending=self.ASCENDING.get(), inplace=True, ignore_index=True)
			self.refill_table()

	def right_click_menu(self, event=None):
		MS = tk.Menu(tearoff=0)
		MS.add_command(label='SORT BY :-', state='disabled')
		for column in self['columns']:
			self.right_click_options[column] = MS.add_command(label = column, command=lambda col=column :self.sort_data(col))
		MS.add_separator()
		MS.add_radiobutton(label='Ascending', variable=self.ASCENDING, value=True, command=lambda :self.sort_data(self.SORT_ORDER))
		MS.add_radiobutton(label='Descending', variable=self.ASCENDING, value=False, command=lambda :self.sort_data(self.SORT_ORDER))
		MS.add_separator()
		MS.add_command(label='Multi Sort', command=lambda:print('Multi Sort'))
		MS.post(event.x_root, event.y_root)

	def get_current(self, search_by=[], get_raw=False):
		curItem = self.focus()
		temp = dict(zip(self['columns'] ,self.item(curItem)['values']))
		if temp=={}:
			raise Exception("Nothing Selected!!")
		if get_raw:
			return temp
		return self.data.loc[self.data.id_by_dict(temp, search_by)].to_dict()

if __name__=="__main__":
	from pandas import DataFrame

	row, column = (0,0)
	root = tk.Tk()
	#root.geometry("320x200")

	df = DataFrame([['Nisar Khan', 'Nisar', 29, 'India'],
					['Abid Shaikh', 'Abid', 40, 'Iran'],
					['Yaqub Jamil', 'Yaqub', 32, 'Pakistan'],
					['Anwar Maqsood', 'Anwar', 37, 'Turkey'],
					['Arbaz Shaikh','Arbaz',25, 'India'],
					['Noman Khan','Noman',34, 'Iran'],
					['Shadab Shafi','Shadab',28, 'Pakistan'],
					['Imran Ashari','Imran',30, 'India'],
					['Fahaad Nafees','Fawad',33, 'Egypt'],
					['Tahir Sultan','Sultan',39, 'India'],
					['Anwar Shehzaad','Anwar',36, 'Turkey']], columns=['Name','Alias','Age','Nation'])

	table_1 = create_treeview(root, sql="select * from fy_list")
	#table_1.data = df
	#table_1.refill_table()
	table_1.grid(row=row, column=column, sticky='nsew')
	row+=2

	def fill_table():
		#print("Clicked Fill table")
		table_1.data.loc[len(table_1.data)] = {"FY_ID":"my_id","FY_NAME":"my_name"}
		table_1.refill_table()

	bn_1 = tk.Button(root, text='Get', command=fill_table) #print(table_1.get_current()))
	bn_1.grid(row=row+1, column=column, ipadx=20)

	root.mainloop()
