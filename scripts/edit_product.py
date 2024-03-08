import pandas as pd

class stock_handle:
	def __init__(self,stock_string,**kwargs):
		self.stock_string = stock_string
		for key,value in kwargs.items():
			setattr(self,key,value)
	
	def stock_iterable(self,inplace=False):
		temp = self.stock_string.split(';')
		if len(temp)%3!=0:
			print(self.stock_string)
			raise Exception('Unexpected length of stock string')
		else:
			pass
		stock_iterable = []
		for i in range(len(temp)//3):
			stock_iterable += [temp[3*i:3*i+3]]
			try:
				stock_iterable[-1][0] = int(stock_iterable[-1][0])
			except:
				stock_iterable[-1][0] = float(stock_iterable[-1][0])
		if not inplace:
			return stock_iterable
		else:
			setattr(self,'stock_iterable',stock_iterable)
		
	def batches(self):
		df = pd.DataFrame(self.stock_iterable(), columns=['QTY', 'BATCH', 'EXP'])
		return df.BATCH.tolist()
		
	def fetch_batch(self,batch):
		temp = self.stock_iterable()
		indx = self.batches().index(batch)
		return temp[indx]
		
	def append_stock(self,stock):		# stock = [qty:int, batch:str, exp:str ('MM/YYYY')]
		new_stock = self.stock_iterable()
		if stock[1] in self.batches():
			new_stock[self.batches().index(stock[1])][0] += stock[0]
		else:
			new_stock += [stock]
		return new_stock
		
	def subtract_stock(self,stock):
		new_stock = self.stock_iterable()
		if stock[1] in self.batches():
			new_stock[self.batches().index(stock[1])][0] -= stock[0]
		else:
			stock[0] = -1*stock[0]
			new_stock += [stock]
		return new_stock
			
	def update(self,stock_iterable):
		for bat in range(len(stock_iterable)):
			stock_iterable[bat][0] = str(stock_iterable[bat][0])
		if len(stock_iterable)==0:
			return ''
		else:
			stock_string = ';'.join(stock_iterable[0])
			if len(stock_iterable)==1:
				return stock_string
			else:
				for batch in stock_iterable[1:]:
					stock_string += ';' + ';'.join(batch)
				self.stock_string = stock_string
				print('New stock string :',stock_string)
				
	def sort_by_exp(self,stock_iterable):
		df = pd.DataFrame(stock_iterable,columns=['QTY','BATCH','EXP'])
		# Write some sorting code
		return df.values.tolist()

class manage_prod:
	def __init__(self, prod_path='sample_database/product_list.csv', stock_path='sample_database/stock_list.csv', **kwargs):
		self.prod_path = prod_path
		self.stock_path = stock_path
		self.stock_data = {}
		self.prod_df = pd.read_csv(prod_path)
		self.stock_df = pd.read_csv(stock_path)
		
		for key,value in kwargs.items():
			setattr(self,key,value)
			
		if hasattr(self,'unit_path'):
			setattr(self,'unit_list',pd.read_csv(unit_path)['UNITS'].tolist())
		
	def reload(self):
		self.prod_df = pd.read_csv(self.prod_path)
		self.stock_df = pd.read_csv(self.stock_path)
		
	def get_index(self,prod_dict,search_for='prod'):
		if not 'ID00' in list(prod_dict.keys()):
			return None
		elif not prod_dict['ID00'] in self.prod_df['ID00'].tolist():
			return None
		elif search_for=='prod':
			return self.prod_df[self.prod_df['ID00']==prod_dict['ID00']].iloc[0].name
		elif search_for=='stock':
			return self.stock_df[self.stock_df['ID00']==prod_dict['ID00']].iloc[0].name
		else:
			return None
		
	def addnew_dict(self,new_dict):
		if ((not 'ID00' in new_dict.keys()) or new_dict['ID00']==''):
			print('KeyError')
			raise KeyError
		if new_dict['ID00'] in self.prod_df['ID00'].tolist():
			print('Exception')
			raise Exception("Cannot make new product, ID00 exists")			
		else:
			self.prod_df.loc[max(list(self.prod_df.index))+1] = new_dict
		
	def editex(self,new_dict):
		ind = self.get_index(new_dict)
		if ind:
			del new_dict['ID00']
			self.prod_df.loc[ind,new_dict.keys()] = new_var.values()
		else:
			raise Exception('Product Entry Not Found')
	
	def get_stock(self,id00,retclass=False):
		stock_string = self.stock_df[self.stock_df['ID00']==id00]['STOCK']
		if len(stock_string)==0:
			stock_string = '0;;'
		else:
			stock_string = stock_string.iloc[0]
		self.stock_data[id00] = stock_handle(stock_string)
		if retclass:
			return stock_handle(stock_string)
		else:
			pass
			
	def update_stock(self,id00):
		stk = self.stock_data[id00].stock_string
		self.stock_df.loc[self.get_index({'ID00':id00},search_for='stock')]['STOCK'] = stk
		del self.stock_data[id00]
		
	def save(self,what='prod',path=None):
		if what=='prod':
			if type(path)!=type('a'):
				path = self.prod_path
			self.prod_df.to_csv(path,index=False)
		elif what=='stock':
			if type(path)!=type('a'):
				path = self.stock_path
			self.stock_df.drop(list(self.stock_df[self.stock_df['']]))
			self.stock_df.to_csv(path,delimiter=',',index=False)
			
'''			
	def add_new_stock(self,id00,new_stock):
		l1 = self.get_stock(id00)
		if len(l1)>0:
			self.stock_df.loc[len(self.stock_df)] = {'ID00':id00,'STOCK':';'.join(l1) + new_stock}
		else:
			self.stock_df.loc[len(self.stock_df)] = {'ID00':id00,'STOCK':new_stock}
			
	def edit_existing_stock(self,id00,new_stock,ind=None):
		record = self.stock_df[self.stock_df['ID00']==id00].index
		if len(record)<1:
			print('No stock available, try adding stock instead!')
		elif len(record)>1:
			print('Unexpected double records found')
		else:
			index = record[0]
			self.stock_df.at[index,'STOCK'] = new_stock
'''
	
if __name__=="__main__":
	print("This script does nothing by itself")

