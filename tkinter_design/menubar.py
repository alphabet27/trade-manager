#!/home/quanta/Apps/anaconda3/bin/python
import os
import pandas as pd
import tkinter as tk
from font import Font_tuple

class menubar:
	def __init__(self,window,filename,tabcontrol=None,font=Font_tuple):
		self.font = font
		self.window = window
		self.filename = filename
		self.tabcontrol = tabcontrol
		self.menu_bar = tk.Menu(self.window)
		self.window.config(menu=self.menu_bar)
		self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.menu_bar.add_cascade(label='File',menu=self.file_menu,font=self.font)
		self.file_menu.add_command(label='Reload',command=lambda:self.restart(filename),font=self.font)
	
	def restart(self,filename):
		self.window.destroy()
		print('Reloading...')
		os.system('python '+filename)


if __name__=='__main__':
	window = tk.Tk()
	window.title('Add/Edit Transactions')
	
	update_button = tk.Button(window,text='Refresh',command=lambda:restart(window,'menubar.py'))
	update_button.grid(row=1,column=0)

	new_label = tk.Label(text='My label is not here')
	new_label.grid(row=0,column=0)
	
	menubar(window,'menubar.py')
	
	window.mainloop()
