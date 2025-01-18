import pandas as pd
import tkinter as tk
from font import main_font
from tkinter import ttk


class combosearch:
	def __init__(self, window, data, **kwargs):
		self.window = window
		self.data = data
		self.nrows = 4
		self.ncols = 2

		for key,value in kwargs.items():
			setattr(self,key,value)

		for key,value in {'ro':0,
						  'col':0,
						  'selectwhat':"",
						  'out':'',
						  'font':main_font,
						  'focus_shift':None}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
			else:
				pass

		#Search Label
		self.l0 = tk.Label(self.window,text='Search :',font=self.font)
		self.l0.grid(column=self.col+0,row=self.ro,padx=10,pady=3,sticky=tk.E)

		#Search button
		self.b0 = tk.Button(self.window,text='Search',command=self.reload_data,font=self.font)
		self.b0.grid(column=self.col+2,row=self.ro,padx=10,pady=3,sticky='ew')

		#Search Box
		self.e0 = tk.Entry(self.window,font=self.font)
		self.e0.grid(column=self.col+1,row=self.ro,padx=0,pady=3,sticky=tk.W)

		# self.ro+=1

		#Select Label
		self.textlabel = tk.Label(self.window, text="Select " + self.selectwhat + " :", font=self.font)
		self.textlabel.grid(row=self.ro+1, column=self.col+0, padx=10, pady=3,sticky=tk.E)

		#Combobox
		self.namechoosen = ttk.Combobox(self.window, width = 27, state="readonly",font=self.font)
		self.namechoosen.grid(row=self.ro+1, column=self.col+1, padx=0, pady=3,sticky=tk.W)

		#Current Selection Label
		self.l3 = tk.Label(self.window,text='Current Selection : ',font=self.font)
		self.l3.grid(row=self.ro+2,column=self.col+0,padx=4,pady=6,sticky=tk.E)

		self.l4 = tk.Label(self.window,text='',font=self.font)
		self.l4.grid(row=self.ro+2,column=self.col+1,padx=3,pady=6,sticky=tk.W)

		#Output Button
		self.b1 = tk.Button(self.window,text='Get Output',command=self.get_output,font=self.font)
		self.b1.grid(row=self.ro+2,column=self.col+2,padx=10,pady=3,sticky = 'ew')

		self.e0.bind('<KeyRelease>',lambda event:self.reload_data())
		self.namechoosen.bind('<FocusOut>',lambda event:self.get_output())
		self.namechoosen.bind('<Return>',lambda event:self.get_output())

		self.reload_data()

	def reload_data(self,relabel=False,addnone=False):
		string = self.e0.get()
		res = [i for i in self.data if string.lower() in i.lower()]
		self.namechoosen['values'] = tuple(res)
		if self.namechoosen.current()==-1:
			res+=['None']
			self.namechoosen.set('None')
		if relabel!=False:
			self.textlabel.config(text='Select ' + self.selectwhat + ' :')
		if addnone:
			self.namechoosen['values'] = self.namechoosen['values'] + ('None',)

	def get_output(self):
		self.l4.config(text=self.namechoosen.get())
		self.out = self.namechoosen.get()
		#print(self.out)

class dual_selector:
	def __init__(self,window,df,**kwargs):
		self.df = df
		self.window = window

		for key,value in kwargs.items():
			setattr(self,key,value)

		for key,value in {'ro':0,
						  'col':0,
						  'out':{},
						  'default':None,
						  'editmode':False,
						  'font':main_font}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
			else:
				pass
		self.options = list(self.df.columns)
		self.option_curr = 0

		self.b1 = tk.Radiobutton(self.window, text='Search by '+self.options[0].lower(),  value=self.options[0], command = lambda:self.fill_labels(0),font=self.font)
		self.b1.grid(row=self.ro,column=self.col, sticky='e', padx=10)

		self.b2 = tk.Radiobutton(self.window, text='Search by '+self.options[1].lower(), value=self.options[1], command = lambda:self.fill_labels(1),font=self.font)
		self.b2.grid(row=self.ro, column=self.col + 1, sticky='w', padx=10)

		self.b3 = tk.Checkbutton(self.window, text='Edit Mode', command=self.mode_switch)
		self.b3.grid(row=self.ro, column=self.col + 2, sticky='w', padx=10)

		self.ro+=1

		self.ss1 = combosearch(self.window,self.df[self.options[self.option_curr]].tolist(),ro=self.ro,col=self.col)
		self.ss1.namechoosen.bind('<FocusOut>', lambda event:self.get_output())
		self.ss1.namechoosen.bind('<Return>', lambda event:self.get_output())
		self.ss1.b1.config(command=self.get_output)

		self.editmode = not self.editmode
		self.fill_labels(self.option_curr)
		self.mode_switch()

	def mode_switch(self):
		if self.editmode:
			self.ss1.e0.config(state='disabled')
			self.ss1.namechoosen.config(state='disabled')
			self.b1.config(state='disabled')
			self.b2.config(state='disabled')
		else:
			self.b1.config(state='normal')
			self.b2.config(state='normal')
			self.ss1.namechoosen.config(state='readonly')
			self.ss1.e0.config(state='normal')
		self.editmode = not self.editmode

	def fill_labels(self,set_curr):
		self.option_curr = set_curr
		self.ss1.e0.delete(0,tk.END)
		self.ss1.data = self.df[self.options[set_curr]].tolist()
		self.ss1.selectwhat = self.options[set_curr]
		self.ss1.reload_data(relabel=True)
		if not len(list(self.out.keys()))==0:
			self.ss1.namechoosen.set(self.out[self.options[set_curr]])
			self.ss1.get_output()
		elif not self.default is None:
			self.ss1.namechoosen.set(self.default[self.options[set_curr]])
			self.ss1.get_output()

	def get_output(self):
		self.ss1.get_output()
		if not self.ss1.out == 'None':
			self.out = self.df[self.df[self.options[self.option_curr]] == self.ss1.out].iloc[0].to_dict()
		elif not self.default is None:
			print(self.default)
			self.ss1.namechoosen.set(self.default[self.options[self.option_curr]])
			self.ss1.l4.config(text=self.ss1.namechoosen.get())
			self.out = self.df[self.df[self.options[self.option_curr]] == self.default[self.options[self.option_curr]]].iloc[0].to_dict()
		else:
			self.out = {}
			print('Not found')

if __name__=="__main__":
	window = tk.Tk()
	window.title('Combobox')

	plista = pd.read_csv('../scripts/sample_database/party_list.csv')

	ss1 = dual_selector(window,plista)

	window.mainloop()
