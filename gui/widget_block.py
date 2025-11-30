import tkinter as tk
from tkinter import ttk
from font import *

class widget_block(tk.Frame):
	def __init__(self, base_frame, entry_dict, *args, combos=None, disabled=None, next_widget=None, shape=None, **kwargs):
		'''
		@entry_dict = The dictionary holding key, value pairs to be entered.
		@base_frame = The base_frame on which the widgets will be placed.
		@ shape[rows, columns]
		@ints, floats = for numeric entries
		'''
		self.base_frame = base_frame
		self.next_widget = next_widget
		self.entry_dict = dict(entry_dict)
		self.disabled = disabled
		self.combos = combos
		self.shape = shape
		self.font = main_font

		super().__init__(base_frame, *args, **kwargs)


		if self.combos is None:
			self.combos = []
		if self.disabled is None:
			self.disabled = []

		self.output = {key : "" for key in self.entry_dict.keys()}

	def labelize(self):
		if self.shape is None:
			self.shape = [len(self.entry_dict.keys())]
		elif (not type(self.shape[0]) is int) or (not type(self.shape[1]) is int):
			raise Exception("Expected int for shape array!")
		elif self.shape[0]*self.shape[1] < len(self.entry_dict.keys()):
			raise Exception("Shape too small for entry!")

		curr_row = 0
		curr_col = 0
		curr_keys = list(self.entry_dict.keys())
		for i, key in enumerate(curr_keys):
			# Make and place the labels
			setattr(self, key + '_l', ttk.Label(self , text = key, font=self.font))
			getattr(self, key + '_l').grid(row = curr_row, column = curr_col, sticky = 'w', padx=10, pady=1)
			# Make and place the entries
			if key in self.combos:
				setattr(self, key + '_e', ttk.Combobox(self, font=self.font, state="readonly"))
				getattr(self, key + '_e')["values"] = self.entry_dict[key]["values"]
			else:
				setattr(self, key + '_e', ttk.Entry(self, font=self.font))
			getattr(self, key + '_e').grid(row = curr_row, column = curr_col + 1, sticky = 'w', padx=10, pady=1)
			# Bind focus shift
			if i<len(curr_keys)-1:
				getattr(self, key + '_e').bind("<Return>", lambda event, j = i : getattr(self, curr_keys[j+1] + '_e').focus_set())
				#getattr(self, key + '_e').bind("<Shift-Return>", lambda event, j = i+1 : getattr(self, curr_keys[j-1] + '_e').focus_set())
			elif not self.next_widget is None:
				getattr(self, key + '_e').bind("<Return>", lambda event : self.next_widget.focus_set())
			# Iterate column pointer
			if (i+1)%self.shape[0]==0:
				curr_row = 0
				curr_col += 2
			else:
				curr_row += 1

	def get_data(self):
		for key in self.entry_dict.keys():
			self.output[key] = getattr(self, key + '_e').get()
		return self.output

	def relabel(self):
		self.clear_entries()
		self.enable_entries(enable_all=True)
		for key, value in self.entry_dict.items():
			if key in self.combos:
				getattr(self, key + '_e').set(value["current"])
				getattr(self, key + '_e')["values"] = value["values"]
			else:
				getattr(self, key + '_e').insert(0, str(value))
		self.disable_entries(disable_all=False)

	def clear_entries(self):
		self.enable_entries(enable_all=True)
		for key in self.entry_dict.keys():
			if not key in self.combos:
				getattr(self, key + '_e').delete(0, 'end')
			if key in self.disabled:
				getattr(self, key + '_e').config(state='disabled')
		self.disable_entries(disable_all=False)

	def enable_entries(self, enable_all=False):
		for key in self.entry_dict.keys():
			if key in self.combos:
				getattr(self, key + '_e').config(state='readonly')
			elif (not key in self.disabled) or enable_all:
				getattr(self, key + '_e').config(state='normal')

	def disable_entries(self, disable_all=True):
		for key in self.entry_dict.keys():
			if disable_all or (key in self.disabled):
				getattr(self, key + '_e').config(state='disabled')


if __name__=="__main__":
	my_data = dict(Name = "Rizwan",
				   Age = 32,
				   Nationality = {"current":"Indian" , "values":["Indian", "Pakistani", "Iraqi"]})
	root = tk.Tk()

	def my_callback(event):
		print("Only numeric value allowed")

	ee = widget_block(root, my_data, combos=["Nationality"], disabled=["Age"], shape=[2,2])
	ee.labelize()
	ee.grid(row=0, column=0)

	#ee.make_numeric('Age', allow_float=False, callback = my_callback)
	def reset():
		global my_data
		new_data = {"Name":my_data["Name"],
					"Age New":my_data["Age"],
					"Nationality":my_data["Nationality"]}
		ee.entry_dict = new_data
		ee.output = dict(new_data)
		ee.labelize()
		ee.relabel()
		new_data = ee.get_data()
		print(len(new_data))

	#ee.disable_entries()

	get_bn = tk.Button(root, text='Get Data', command=lambda:print(ee.get_data()))
	get_bn.grid(row=1, column=2)

	set_bn = tk.Button(root, text='Set Data', command=reset)
	set_bn.grid(row=2, column=2)

	root.mainloop()
