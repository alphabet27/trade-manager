import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import Font_tuple
from menubar import menubar
from transaction_make import transact_frame
from manage_party_class import manage_party_class
from manage_product_class import manage_product_class

class main_window:
	def __init__(self,window,menubar=None,*args):
		self.n_tabs = 0
		self.window = window
		self.menubar = menubar
		self.tabControl = ttk.Notebook(self.window) 
		self.tabControl.grid(row=0,column=0)
		
	def add_tab(self,label,tab_name,tab_class,*args,**kwargs):
		'''
			label 		= Name mentioned on top + Name with which "tab_variable" will be referred
			tab_name 	= Name with which initiated tab_class will be referred
			*args 		= Args to pass to the tab_class
			**kwargs	= Kwargs to pass to the tab_class
		'''
		if not 'init_command' in kwargs.keys():
			init_command = None
		setattr(self,label,tk.Frame(self.tabControl))
		self.tabControl.add(getattr(self,label), text=label)
		setattr(self,tab_name,tab_class(getattr(self,label),*args,**kwargs))
		
		if type(init_command)!=type(None):
			getattr(getattr(self,tab_name),init_command)()
		self.n_tabs+=1

if __name__ == "__main__":
	window = tk.Tk()
	window.title("Main Window")
	upper_menu = menubar(window,filename='main_window.py')

	win_main = main_window(window)
	
	prod_path = '../scripts/sample_database/product_list.csv'
	stock_path = '../scripts/sample_database/product_stock.csv'
	
	win_main.add_tab('Product_Manager','prod_class',manage_product_class,prod_path,stock_path,font=Font_tuple)

	win_main.tab2 = tk.Frame(win_main.tabControl)
	l2 = tk.Label(win_main.tab2, text ="This is a second window \n For other modules like \n\t'party_manager' \n\t 'transaction_make'\nrefer the tkinter_design folder")
	l2.grid(column = 0, row = 0, padx = 30, pady = 30, sticky='e')
	win_main.tabControl.add(win_main.tab2, text ='Tab 2') #,font=Font_tuple)

	window.mainloop()
