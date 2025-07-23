import sql_backend as sqlb
from widget_block import *

class selector(tk.Frame):
	def __init__(self, base_frame, sql_query, *args, next_widget=None, keys=None, shape=None, **kwargs):
		self.base_frame = base_frame
		self.sql_query = sql_query
		self.data = sqlb.SQL_DataFrame(con = sqlb.get_connection(), sql=sql_query)
		self.keys = keys
		self.shape = shape
		self.output = None
		self.next_widget = next_widget

		super().__init__(base_frame, *args, **kwargs)

		self.edit_mode = tk.BooleanVar(self)
		self.current_key = tk.StringVar(self)
		self.current_index = tk.IntVar(self)

		if self.keys is None:
			self.keys = list(self.data.columns)

		if shape is None:
			self.shape = [1, len(self.keys)]
		elif (not type(shape[0]) is int) or (not type(shape[1]) is int):
			raise Exception("Expected int for shape array!")
		elif self.shape[0]*self.shape[1] < len(keys):
			raise Exception("Shape too small for keys!")

		if keys is None:
			self.keys = [self.data.columns[0]]

		self.current_key.set(self.keys[0])

		self.mode_button = tk.Checkbutton(self, text='Unlock', command=self.mode_switch, variable = self.edit_mode, background='yellow')
		self.mode_button.grid(row=1, column=self.shape[-1], padx=10, pady=2, sticky='nsew')

		self.search_label = tk.Label(self, text='Search')
		self.search_label.grid(row=self.shape[0]+1, column=0, sticky='e', padx=10, pady=2)

		self.search_box = ttk.Combobox(self)
		self.search_box.bind("<KeyRelease>", self.filter_list)
		self.search_box.bind("<Return>", self.get_data)
		self.search_box.grid(row=self.shape[0]+1, column=1)

		self.select_button = tk.Button(self, text = 'Select', command=self.get_data)
		self.select_button.grid(row=self.shape[0]+1, column=2, padx=10, sticky='nsew')

		self.reload_button = tk.Button(self, text = '\u27f2', command=self.reload_data, fg="blue", font=("bold",12))
		self.reload_button.grid(row=self.shape[0]+1, column=3, sticky='nsew')

		self.labelize()
		self.mode_switch()
		self.filter_list()

	def reload_data(self):
		self.data = sqlb.SQL_DataFrame(con = sqlb.get_connection(), sql=self.sql_query)
		self.filter_list()

	def labelize(self):
		curr_row = 1
		curr_col = 0
		for i, key in enumerate(self.keys):
			setattr(self, key + '_sel', tk.Radiobutton(self, text='Search by '+key, command = lambda : self.filter_list(new_key = True), variable = self.current_key, value = key))
			getattr(self, key + '_sel').grid(row = curr_row, column = curr_col, padx=10, pady=2)
			if (i+1)%self.shape[0]==0:
				curr_row = 1
				curr_col += 1
			else:
				curr_row += 1


	def filter_list(self, event=None, new_key=False):
		key = self.current_key.get()
		options = self.data[key].to_list()
		if new_key:
			if not self.output is None:
				self.search_box.set(self.output[key])
			else:
				self.search_box.set('')
		substring = self.search_box.get()
		for item in self.data[key]:
			if not substring.lower() in str(item).lower():
				options.remove(item)
		self.search_box['values'] = options

	def get_data(self, event=None):
		try:
			self.output = self.data.scan(self.current_key.get(), self.search_box.get(), isunique=True)
		except:
			self.output = None
		if not self.next_widget is None:
			self.next_widget.focus_set()

	def set_data(self, key, value):
		self.current_key.set(key)
		self.output = self.data.scan(key, value, isunique=True)
		self.filter_list(new_key=True)

	def mode_switch(self):
		new_state = 'disabled'
		if self.edit_mode.get():
			new_state = 'normal'
		for key in self.keys:
			getattr(self, key + '_sel').config(state = new_state)
		self.search_box.config(state = new_state)

if __name__=="__main__":
	root = tk.Tk()

	# df = DataFrame([['Nisar Khan', 'Nisar', 29],
	# 				['Abid Shaikh', 'Abid', 40],
	# 				['Yaqub Jamil', 'Yaqub', 32],
	# 				['Anwar Maqsood', 'Anwar', 37]], columns=['Name','Alias','Age'])

	sel_1 = selector(root, "select * from fy_list") #, keys=['PARTY_NAME','ALIAS'])
	sel_1.grid(row=0, column=0)
	print(sel_1.data)
	#sel_1.select_button.config(command = lambda sel = sel_1:sel.lift())
	root.mainloop()
