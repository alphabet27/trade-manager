#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from menubar import *
from font import Font_tuple
from tkinter import ttk

''' Modify default selector to select from dictionary '''
	
''' Try <FocusOut> and/or <KeyboardFocusOut> for preventing combobox from collapsing when cursor moves to search 	 field and hence make a better version. '''

class combosearch:
	def __init__(self, window, **kwargs):
		self.window = window
		self.nrows = 4
		self.ncols = 2
		
		for key,value in kwargs.items():
			setattr(self,key,value)
			
		for key,value in {'plist':[], 
						  'ro':0, 
						  'col':0, 
						  'selectwhat':"Party", 
						  'out':'', 
						  'addnone':False, 
						  'font':Font_tuple, 
						  'focus_shift':None}.items():
			if not hasattr(self,key):
				setattr(self,key,value)
			else:
				pass

	def getparty(self):
		self.l2.config(text=self.namechoosen['values'][self.namechoosen.current()],font=self.font)
		self.out = self.namechoosen['values'][self.namechoosen.current()]
	
	def reload_data(self,relabel=False):
		string = self.e1.get()
		res = [i for i in self.plist if string.lower() in i.lower()]
		self.namechoosen['values'] = tuple(res)
		if relabel!=False:
			self.l1.config(text='Select ' + self.selectwhat + ' :')
		if self.addnone:
			self.namechoosen['values'] = self.namechoosen['values'] + ('None',)
    # label
	def labelize(self):
		self.l0 = tk.Label(self.window,text='Search :',font=self.font)
		self.l0.grid(column=self.col+0,row=self.ro+1,padx=10,pady=3,sticky=tk.E)

    # button
		self.b0 = tk.Button(self.window,text='Search',command=self.reload_data,font=self.font)
		self.b0.grid(column=self.col+2,row=self.ro+1,padx=10,pady=3,sticky=tk.W)

    #Entry
		self.e1 = tk.Entry(self.window,font=self.font)
		self.e1.grid(column=self.col+1,row=self.ro+1,padx=0,pady=3,sticky=tk.W)
		self.textlabel = "Select " + self.selectwhat + " :"

    # label
		self.l1 = tk.Label(self.window, text = self.textlabel,font=self.font)
		self.l1.grid(column = self.col + 0,row = self.ro + 2, padx = 10, pady = 3, sticky=tk.E)

    # Combobox creation
		self.namechoosen = ttk.Combobox(self.window, width = 27, state="readonly",font=self.font)

    # Adding combobox drop down list
		self.namechoosen['values'] = tuple(self.plist)
		
		if self.addnone:
			self.namechoosen['values'] = self.namechoosen['values'] + ('None',)

		self.namechoosen.grid(column = self.col + 1, row = self.ro + 2, sticky='w')
		self.namechoosen.current()

		self.l3 = tk.Label(self.window,text='Current Selection : ',font=self.font)
		self.l3.grid(row=self.ro+3,column=self.col+0,padx=3,pady=6,sticky=tk.E)

		self.l2 = tk.Label(self.window,text='',font=self.font)
		self.l2.grid(row=self.ro+3,column=self.col+1,padx=0,pady=3,sticky=tk.W)

    #Print
		#def getparty(addon=None):
		#	self.l2.config(text=self.namechoosen['values'][self.namechoosen.current()])
		#	self.out = self.namechoosen['values'][self.namechoosen.current()]
		
		self.b1 = tk.Button(self.window,text='Print Current',command=self.getparty,font=self.font)
		self.namechoosen.bind('<Return>',self.getparty)
		self.b1.grid(row=self.ro+3,column=self.col+2,padx=10,pady=3,sticky = 'w')
		
		#self.ro+=4
		
	def getparty(self):
		self.l2.config(text=self.namechoosen['values'][self.namechoosen.current()])
		self.out = self.namechoosen['values'][self.namechoosen.current()]
		if type(self.focus_shift)!=type(None):
			pass		# Define focus shifting event later
		
		
    # Takes 4 rows and 2 columns to run in total. Start from 5th row or 3rd column
    
class multi_selector:
	def __init__(self,window,df,ro=0,col=0,default=None,**kwargs):
		self.df = df
		self.ro = ro
		self.col = col
		self.default = default
		self.window = window
		self.out = {}
		
		for key,value in kwargs.items():
			setattr(self,key,value)
		if not hasattr(self,'font'):
			self.font = Font_tuple
		
		self.options = list(self.df.columns)
		self.v1 = tk.StringVar(self.window,self.options[0])

		self.b1 = tk.Radiobutton(self.window, text='Search by '+self.options[0].lower(), variable=self.v1, value=self.options[0], command=self.fill_labels,font=self.font)
		self.b1.grid(row=self.ro,column=self.col, sticky='e', padx=10)
		self.b2 = tk.Radiobutton(self.window, text='Search by '+self.options[1].lower(), variable=self.v1, value=self.options[1], command=self.fill_labels,font=self.font)
		self.b2.grid(row=self.ro,column=self.col + 1, sticky='w', padx=10)

		self.ss1 = combosearch(self.window,plist = self.df[self.v1.get()].tolist(), ro=self.ro+1,col=self.col, selectwhat=self.v1.get()[0] + self.v1.get()[1:-2].lower(), **kwargs)
		self.ss1.labelize()
		
		self.ss1.b1.config(command=self.get_output)
		self.ss1.namechoosen.bind('<Return>',lambda event:self.get_output())
		
		self.ss1.e1.bind('<KeyRelease>',lambda event:self.ss1.reload_data())
		
	def fill_labels(self):
		self.ss1.e1.delete(0,tk.END)
		self.ss1.plist = self.df[self.v1.get()].tolist()
		self.ss1.selectwhat = self.v1.get()[0] + self.v1.get()[1:].lower()
		self.ss1.reload_data(relabel=True)
		if not self.default is None:
			try:
				self.set_default(self.default)
			except:
				print('Some error occurred')
		
	def get_output(self):
		self.ss1.getparty()
		self.out = {self.v1.get():self.ss1.out}
		if not (self.ss1.addnone and (self.ss1.out=='None')):
			for option in self.options:
				if option!=self.v1.get():
					temp = self.df[self.df[self.v1.get()]==self.ss1.out]
					# print('temp indices \n',temp.iloc[list(temp.index)[0]])	# Indexing always starts from 0
					self.out[option] = temp.iloc[0][option]
				else:
					pass
			key_order = list(self.df.columns)
			ordered_dict = {k: self.out[k] for k in key_order}
			self.out = ordered_dict
			print('Recieved',list(self.out.values()))
		else:
			print('Recieved None')
			
	def set_default(self,keyval):
		self.default = keyval
		#print(self.ss1.namechoosen.current())
		self.ss1.namechoosen.current(list(self.ss1.namechoosen['values']).index(keyval[self.v1.get()]))
		#self.ss1.event_generate('<Return>')

#print(__name__)  -- gives combo_search

if __name__=="__main__":
	plista = pd.read_csv('../scripts/sample_database/party_list.csv')['ALIAS00'].tolist()
	plistb = pd.read_csv('../scripts/sample_database/party_list.csv') #,usecols=['ALIAS00','PARTY00'])
	
	window = tk.Tk()
	window.title('Combobox')
	#window.geometry('500x250')
	
	menubar(window,'combo_search.py')
	
	ro1 = 0
	col1 = 0

	#ss1 = combosearch(window,plist=plista,selectwhat='Party',ro=ro1,col=col1)
	#ss1.labelize()
	
	ss2 = multi_selector(window,plistb,ro=ro1+1, addnone=True)
	ss2.set_default({'ALIAS00':'alias04','PARTY0':'party04'})
	
	window.mainloop()
  
	


