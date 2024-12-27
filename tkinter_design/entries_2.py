import tkinter as tk
from tkinter import ttk
from font import main_font

class entries:
	def __init__(self,window,edict={},ro=0,col=0,warnfunc=None,font=main_font):
		self.warnfunc = warnfunc
		self.window = window
		self.numerics = []
		self.floats = []
		self.edict = edict
		self.font = font
		self.col = col
		self.ro = ro

		for i in range(len(self.edict)):
			setattr(self,'lab'+str(i),tk.Label(self.window,text=list(self.edict.keys())[i] + ' : ',font=self.font))
			getattr(self,'lab'+str(i)).grid(row=self.ro+i,column=self.col,sticky=tk.E,padx=5)
			setattr(self,'ent'+str(i),tk.Entry(self.window,font=self.font))
			getattr(self,'ent'+str(i)).grid(row=self.ro+i,column=self.col+1,sticky=tk.W,padx=5,pady=3)
			if i+1<len(self.edict):	# How to pass by value to lambda function??
				getattr(self,'ent'+str(i)).bind('<Return>',lambda event,j=i: self.focus_shift(j))

	def relabel(self):
		self.clear_entries()
		for i in range(len(self.edict)):
			getattr(self,'ent'+str(i)).insert(0,str(list(self.edict.values())[i]))

	def disable_entries(self):
		for i in range(len(self.edict)):
			getattr(self,'ent'+str(i)).config(state='disabled')

	def enable_entries(self):
		for i in range(len(self.edict)):
			getattr(self,'ent'+str(i)).config(state='normal')

	def clear_entries(self):
		for i in range(len(self.edict)):
			_ = getattr(self,'ent'+str(i)).get()
			for j in range(len(_)):
				getattr(self,'ent'+str(i)).delete(0)

	def make_numeric(self,index,allowfloat=False,warnfunc=None):
		def callback(index):
			string = getattr(self,'ent'+str(index)).get()
			if len(string)>0:
				if string[0]=='-':
					string=string[1:]
			ndots = string.split('.')
			case1 = (len(ndots)>2)
			case2 = (False in [((ndots[_].isnumeric()) or (ndots[_]=='')) for _ in range(len(ndots))])
			if (((not allowfloat) and (not (string.isnumeric() or string==''))) or (allowfloat and (case1 or case2))):
				getattr(self,'ent'+str(index)).delete(0,tk.END)
				print('Locals string, ndots, case1, case2 :',string,ndots,case1,case2)
				if allowfloat and (not (warnfunc is None)):
					warnfunc('float')
				elif (not allowfloat) and (not (warnfunc is None)):
					warnfunc('int')
		getattr(self,'ent'+str(index)).bind('<KeyRelease>',lambda event:callback(index))
		if not allowfloat:
			self.numerics.append(index)
		else:
			self.floats.append(index)

	def get_entries(self):
		ent_list = []
		for i in range(len(self.edict)):
			temp = (getattr(self,'ent'+str(i))).get()
			if i in self.numerics:
				if ((temp == '') or (temp == '.')):
					temp = '0'
				ent_list = ent_list + [int(temp)]
			elif i in self.floats:
				if ((temp == '') or (temp == '.')):
					temp = '0'
				ent_list = ent_list + [float(temp)]
			else:
				ent_list = ent_list + [temp]
		return dict(zip(list(self.edict.keys()),ent_list))

	def focus_shift(self,i):
		getattr(self,'ent'+str(i+1)).focus_set()

if __name__=='__main__':
	def my_fun(errtype):
		r1 = tk.Tk()
		l1 = tk.Label(r1,text='Only '+errtype+' is allowed')
		l1.grid(row=0,column=0)
		r1.mainloop()
	root = tk.Tk()
	data = {'Name':'', 'Age':'', 'Nationality':''}
	ee01 = entries(root,data,warnfunc=my_fun)
	ee01.make_numeric(1)
	root.mainloop()
