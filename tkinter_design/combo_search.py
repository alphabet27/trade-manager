#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from menubar import *
from font import Font_tuple
from tkinter import ttk

''' Define a multi column selector as used in the "manage_product_class.py" & "manage_party_class.py"
	This will reduce code in those scripts and make them more readable. '''

class combosearch:
	def __init__(self,window,plist=[],ro=0,col=0,selectwhat="Party",out='',font=Font_tuple):
		self.window = window
		self.ro = ro
		self.col = col
		self.out = out
		self.nrows = 4
		self.ncols = 2
		self.font = font
		self.plist = plist
		self.selectwhat = selectwhat

	def getparty(self):
		self.l2.config(text=self.namechoosen['values'][self.namechoosen.current()],font=self.font)
		self.out = self.namechoosen['values'][self.namechoosen.current()]
	
	def reload_data(self,relabel=False):
		string = self.e1.get()
		res = [i for i in self.plist if string.lower() in i.lower()]
		self.namechoosen['values'] = tuple(res)
		if relabel!=False:
			self.l1.config(text='Select ' + self.selectwhat + ' :')
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

		self.namechoosen.grid(column = self.col + 1, row = self.ro + 2)
		self.namechoosen.current()

		self.l3 = tk.Label(self.window,text='Current Selection : ',font=self.font)
		self.l3.grid(row=self.ro+3,column=self.col+0,padx=3,pady=6,sticky=tk.W)

		self.l2 = tk.Label(self.window,text='',font=self.font)
		self.l2.grid(row=self.ro+3,column=self.col+1,padx=0,pady=3,sticky=tk.W)

    #Print
		def getparty():
			self.l2.config(text=self.namechoosen['values'][self.namechoosen.current()])
			self.out = self.namechoosen['values'][self.namechoosen.current()]
		#        global selection 
		#        selection = selection + [namechoosen['values'][namechoosen.current()]]
		#        print(selection)

		self.b1 = tk.Button(self.window,text='Print Current',command=getparty,font=self.font)
		self.b1.grid(row=self.ro+3,column=self.col+2,padx=10,pady=3,sticky = 'w')
		
		self.ro+=4
    # Takes 4 rows and 2 columns to run in total. Start from 5th row or 3rd column
    
class multi_selector:
	def __init__(self,window,df,ro=0,col=0,**kwargs):
		self.df = df
		self.ro = ro
		self.col = col
		self.window = window
		for key,value in kwargs.items():
			setattr(self,key,value)
		if not hasattr(self,'font'):
			self.font = Font_tuple
		
		self.options = list(self.df.columns)
		self.v1 = tk.StringVar(self.window,self.options[0])

		self.b1 = tk.Radiobutton(self.window, text='Search by '+self.options[0].lower(), variable=self.v1, value=self.options[0], command=self.fill_labels,font=self.font)
		self.b1.grid(row=self.ro,column=self.col)
		self.b2 = tk.Radiobutton(self.window, text='Search by '+self.options[1].lower(), variable=self.v1, value=self.options[1], command=self.fill_labels,font=self.font)
		self.b2.grid(row=self.ro,column=self.col + 1)

		self.ss1 = combosearch(self.window,plist = self.df[self.v1.get()].tolist(), ro=self.ro+1,col=self.col, selectwhat=self.v1.get()[0] + self.v1.get()[1:-2].lower())
		self.ss1.labelize()
		
	def fill_labels(self):
		self.ss1.e1.delete(0,tk.END)
		self.ss1.plist = self.df[self.v1.get()].tolist()
		self.ss1.selectwhat = self.v1.get()[0] + self.v1.get()[1:-2].lower()
		self.ss1.reload_data(relabel=True)

#print(__name__)  -- gives combo_search

if __name__=="__main__":
	plista = pd.read_csv('../scripts/sample_database/party_list.csv')['ALIAS00'].tolist()
	plistb = pd.read_csv('../scripts/sample_database/party_list.csv',usecols=['ALIAS00','PARTY00'])
	
	window = tk.Tk()
	window.title('Combobox')
	#window.geometry('500x250')
	
	menubar(window,'combo_search.py')
	
	ro1 = 0
	col1 = 0

	ss1 = combosearch(window,plist=plista,selectwhat='Party',ro=ro1,col=col1)
	ss1.labelize()
	
	ss2 = multi_selector(window,plistb,ro=ss1.ro+1)
	
	window.mainloop()
  
	


