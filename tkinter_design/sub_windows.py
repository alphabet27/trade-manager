import tkinter as tk
import tkinter.scrolledtext as st
import traceback as trc_back
from entries_2 import entries
from font import *

class quick_add_window:
	def __init__(self,base_win,output={},font=main_font):
		self.base_win = base_win
		self.save_succ = False
		self.font = main_font
		self.qa_root = tk.Toplevel(self.base_win)
		self.qa_vals = {'BATCH':'','EXP':'','QTY':'','MRP':''}
		self.output = {}
		self.qa_entries = entries(self.qa_root, edict=self.qa_vals)
		self.qa_entries.make_numeric(2)
		self.qa_entries.make_numeric(3,allowfloat=True)
		#Add Button
		self.qa_button = tk.Button(self.qa_root,text='Add',command=self.add_data)
		self.qa_button.grid(row=3,column=2,ipadx=30,padx=10)
		self.qa_root.transient(self.base_win)
		self.qa_root.grab_set()
		self.base_win.wait_window(self.qa_root)

	def add_data(self):
		self.output = self.qa_entries.get_entries()
		print('Quick add returned',self.output)	#Add this to stock_manager
		self.qa_root.destroy()
		self.save_succ = True

	def launch(self):
		self.window.transient(self.base_win)
		self.window.grab_set()
		self.base_win.wait_window(self.window)

class exit_conf:
	def __init__(self, base_win, istab = {'val':False, 'tabctrl':None, 'tablist':None, 'tab_id':None}, isroot=False, text='Close without saving?', font=main_font):
		self.base_win = base_win
		self.font = main_font
		self.isroot = isroot
		self.istab = istab

		self.conf = tk.Toplevel(self.base_win)
		self.conf.title('Exit?')
		self.warn_label = tk.Label(self.conf,text=text)
		self.warn_label.grid(row=0,column=0,sticky='ew',columnspan=2,ipadx=2,pady=10)
		self.yes_button = tk.Button(self.conf,text='Yes', command=self.destroyer,font=self.font)
		self.yes_button.grid(row=1,column=0,sticky='ew',padx=1,ipadx=30,pady=1)
		self.no_button = tk.Button(self.conf,text='No',command=self.conf.destroy,font=self.font)
		self.no_button.grid(row=1,column=1,sticky='ew',padx=1,ipadx=30,pady=1)
		self.conf.transient(self.base_win)
		self.conf.grab_set()
		self.base_win.wait_window(self.conf)
		#self.conf.mainloop()

	def destroyer(self):
		try:
			self.conf.destroy()
			if self.isroot:
				self.base_win.quit()	# You might need to do other way round - destroy then quit
			if not self.istab['val']:
				self.base_win.destroy()
			else:
				self.istab['tabctrl'].forget(self.istab['tab_id'])
				self.istab['tablist'].remove('tab_id')# Add the "Notebook(TabControl)" instead of base window
		except:
			self.conf.destroy()

class billno_window:
	def __init__(self,base_win,billno_default):
		self.value = tk.IntVar()
		self.base_win = base_win
		self.billno_default = billno_default
		self.bwin = tk.Toplevel(self.base_win)
		self.bn_lab = tk.Label(self.bwin, text='Enter Bill No. :', font=main_font)
		self.bn_lab.grid(row=0, column=0, sticky='e',padx=10)
		self.sp1 = tk.Spinbox(self.bwin,from_=1,to=9999,textvariable=self.value, font=main_font)
		self.sp1.grid(row=0,column=1,columnspan=2,pady=20,padx=10,sticky='w')
		self.value.set(billno_default)
		self.acc = tk.Button(self.bwin,text='Accept',command=self.bwin.destroy)
		self.acc.grid(row=6,column=1,ipadx=20,pady=5)
		self.bwin.transient(self.base_win)
		self.bwin.grab_set()
		self.base_win.wait_window(self.bwin)

class error_message:
	def __init__(self,excp,msg,traceback):
		self.erm_box = tk.Tk()
		self.erm_box.title("Error")
		self.val1 = tk.Label(self.erm_box,text=str(msg),font=main_font)
		self.val1.grid(row=0,column=0,columnspan=2,padx=10,pady=10)
		self.tb_box = st.ScrolledText(self.erm_box,width=40,height=8,font=main_font)
		self.tb_box.grid(row=1,column=0,columnspan=2,rowspan=2,padx=10,sticky='nsew')
		#trc_msg =
		self.tb_box.insert(tk.INSERT,str(trc_back.extract_tb(traceback)))
		self.tb_box.config(state='disabled')
		self.ok = tk.Button(self.erm_box,text='Okay',command=self.erm_box.destroy,font=main_font)
		self.ok.grid(row=3,column=1,padx=10,pady=10,ipadx=20,sticky='e')
		self.erm_box.grid_rowconfigure(1,weight=1)
		self.erm_box.grid_columnconfigure(1,weight=1)
		self.erm_box.mainloop()

class multi_sort:
	def __init__(self):
		pass
	# Make the multi sort window

if __name__=='__main__':
	base = tk.Tk()
	def billwin():
		bb1 = billno_window(base,billno_default=32)
		print('Closed bb1')
		print(bb1.value.get())
	b1 = tk.Button(base,text='Open',command=billwin)
	b1.grid(row=0,column=0,padx=20,pady=20)
	base.mainloop()
