import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk
from font import main_font
from sub_windows import error_message
from party_editor import party_class
from product_editor import product_class
from transaction_list import transaction_frame

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

class menubar:
	def __init__(self,window,notebook,database,filename,attr_main={},font=main_font):
		self.font = font
		self.window = window
		self.filename = filename
		self.database = database
		self.tabControl = notebook
		self.attr_main = attr_main
		self.menu_bar = tk.Menu(self.window)
		self.window.config(menu = self.menu_bar)
		#
		self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.data_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.trsc_menu = tk.Menu(self.menu_bar, tearoff=0)
		#
		self.menu_bar.add_cascade(label='File', menu = self.file_menu, font = self.font)
		self.menu_bar.add_cascade(label='Database', menu = self.data_menu, font = self.font)
		self.menu_bar.add_cascade(label='Transactions', menu = self.trsc_menu, font = self.font)
		#
		self.file_menu.add_command(label='Reload',command=lambda:self.restart(filename),font=self.font)
		self.data_menu.add_command(label='Account Manager',command=lambda:self.nb_add('acc_man', party_class))
		self.data_menu.add_command(label='Inventory Manager',command=lambda:self.nb_add('inv_man', product_class))
		self.trsc_menu.add_command(label='Transactions Manager',command=lambda:self.nb_add('trsc_man', transaction_frame))
	
	def restart(self,filename):
		self.window.destroy()
		print('Reloading...')
		exec_path = sys.executable
		os.system('"' + exec_path + '"' + ' ' + filename)

	def nb_add(self, tab_name, tab_class, *args, **kwargs):
		self.attr_main[tab_name] = tab_class(tab_name, self.tabControl, self.database, self.attr_main, *args, **kwargs)

	def nb_remove(self, tab_name):
		if not tab_name in self.attr_main.keys():
			print('No such tab')
		elif hasattr(self.attr_main[tab_name],'sub_frames'):
			if not len(self.attr_main[tab_name].sub_frames)==0:
				raise Exception("Close active tabs "+str(self.attr_main[tab_name].sub_frames))
		else:
			del self.attr_main[tab_name]



if __name__=='__main__':
	window = tk.Tk()
	try:
		window.state('zoomed')
	except:	
		window.attributes('-zoomed', True)
	window.title('TRADE MANAGER MAIN WINDOW')
	
	tabctrl = ttk.Notebook(window)
	tabctrl.pack(fill = tk.BOTH, expand = True)

	upper_menu = menubar(window,tabctrl,database,'main_window.py')

	window.report_callback_exception = lambda exc=None,msg=None,tb=None:error_message(exc,msg,tb)
	window.mainloop()
