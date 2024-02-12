import tkinter as tk
from tkinter import ttk
from font import Font_tuple	

class confirm_exit:
	def __init__(self,what,mytext='Close without saving?',font=Font_tuple):
		self.what = what
		self.conf = tk.Tk()
		self.conf.title('Exit?')
		self.warn_label = tk.Label(self.conf,text=mytext)
		self.warn_label.grid(row=0,column=0,sticky='ew',columnspan=2,padx=10,pady=10)
		self.yes_button = tk.Button(self.conf,text='Yes',command=self.destroyer(),font=self.font)
		self.yes_button.grid(row=1,column=0,sticky='ew')
		self.no_button = tk.Button(self.conf,text='No',command=self.conf.destroy,font=self.font)
		self.no_button.grid(row=1,column=1,sticky='ew')
		self.conf.mainloop()
		
	def destroyer(self):
		self.what.destroy()
		self.conf.destroy()
		
