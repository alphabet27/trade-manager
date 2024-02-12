#!/home/quanta/Apps/anaconda3/bin/python
import pandas as pd
import tkinter as tk
from font import Font_tuple

class entries:
	def __init__(self,window,hlist=[],elist=[],ro=0,col=0,numerics=None,font=Font_tuple):
		self.numerics = list([])
		self.window = window
		self.hlist = hlist
		self.elist = elist
		self.font = font
		self.col = col
		self.ro = ro
		
	def disable_entries(self):
		for i in range(len(self.elist)):
			getattr(self,'ent'+str(i)).config(state='disabled')
		
	def enable_entries(self):
		for i in range(len(self.elist)):
			getattr(self,'ent'+str(i)).config(state='normal')
		
	def clear_entries(self):
		for i in range(len(self.hlist)):
			_ = getattr(self,'ent'+str(i)).get()
			for j in range(len(_)):
				getattr(self,'ent'+str(i)).delete(0)
			
	def get_entries(self):
		ent_list = []
		for i in range(len(self.hlist)):
			if i in self.numerics:
				ent_list = ent_list + [int(getattr(self,'ent'+str(i)).get())]
			else:
				ent_list = ent_list + [getattr(self,'ent'+str(i)).get()]
		return ent_list
		
	def get_dict(self):
		return dict(zip(self.hlist,self.get_entries()))
		
	def labelize(self):
		for i in range(len(self.hlist)):
			setattr(self,'lab'+str(i),tk.Label(self.window,text=self.hlist[i] + ' : ',font=self.font))
			getattr(self,'lab'+str(i)).grid(row=self.ro+i,column=self.col,sticky=tk.E,padx=5)
			setattr(self,'ent'+str(i),tk.Entry(self.window,font=self.font))
			getattr(self,'ent'+str(i)).grid(row=self.ro+i,column=self.col+1,sticky=tk.W,padx=5,pady=3)
			#Focus Shifting Event
			if i>0:
				getattr(self,'ent'+str(i-1)).bind('<Return>',lambda event:getattr(self,'ent'+str(i)).focus_set())
		self.relabel()
		self.ro+=len(self.elist)
		
	def make_numeric(self,index):
		def callback(index):
			string = getattr(self,'ent'+str(index)).get()
			if not string.isnumeric():
				getattr(self,'ent'+str(index)).delete(0,tk.END)
				#getattr(self,'ent'+str(index)).insert(0,new_string)	#Use if you define a number filter
		getattr(self,'ent'+str(index)).bind('<KeyRelease>',lambda event:callback(index))
		self.numerics.append(index)
	
	def relabel(self):
		self.clear_entries()
		for i in range(len(self.elist)):
			getattr(self,'ent'+str(i)).insert(0,str(self.elist[i]))
			
if __name__ == "__main__":
	window = tk.Tk()
	ee = entries(window,hlist = ['Person Name','Person Age','Person Nationality','Person Occupation'], elist=['','','Indian',''])
	ee.labelize()
	print("Showing sample of entry widget")
	
	def sample_insert(ee):
		ee.elist = ['Rizwan','24','Indian','Student']
		ee.relabel()
		var1 = ee.get_entries()
		print('Recieved',var1)
		
	def get_it(ee):
		var1 = ee.get_entries()
		print('Recieved',var1)
	
	b1 = tk.Button(window,text='Clear',command=ee.clear_entries,font=Font_tuple)
	b1.grid(row=0,column=2,padx=5,sticky=tk.W)
	b2 = tk.Button(window,text='Fillit',command=lambda:sample_insert(ee),font=Font_tuple)
	b2.grid(row=1,column=2,padx=5,sticky=tk.W)
	b3 = tk.Button(window,text='Getit',command=lambda:get_it(ee),font=Font_tuple)
	b3.grid(row=2,column=2,padx=5,sticky=tk.W)
	b4 = tk.Button(window,text='Do Nothing',command=lambda:print('ee'),font=Font_tuple)
	b4.grid(row=3,column=2,padx=5,sticky=tk.W)
	window.mainloop()
