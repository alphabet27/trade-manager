import json
import pandas as pd

# Check units data later

class stock_handle:
	def __init__(self,pid,stock_json):
		self.pid = pid
		self.stock_json = stock_json
		self.stock_info = json.loads(self.stock_json)

	def increase(self,batch,by_n):
		if not batch in self.stock_info.keys():
			raise Exception('Requested batch not found')
		else:
			self.stock_info[batch]['QTY']+=by_n

	def decrease(self,batch,by_n,remove_null=True):
		if not batch in self.stock_info.keys():
			raise Exception('Requested batch not found')
		else:
			self.stock_info[batch]['QTY']-=by_n
		popables = []
		if remove_null:
			for key,value in self.stock_info.items():
				if value['QTY']==0:
					popables.append(key)
				else:
					pass
			for popable in popables:
				_=self.stock_info.pop(popable)

	def update_dict(self,sd):
		if sd['BATCH'] in list(self.stock_info.keys()):
			self.stock_info[sd['BATCH']]['QTY']+=sd['QTY']
		else:
			temp = sd.pop('BATCH')
			self.stock_info.update({temp:sd})

	def update_json(self):
		self.stock_json = json.dumps(self.stock_info)

class manage_prod:
	def __init__(self, database,**kwargs):
		self.product_path = database['product_path']
		self.prod_df = pd.read_csv(self.product_path)

		for key,value in kwargs.items():
			setattr(self,key,value)

		#if hasattr(self,'unit_path'):
		#	setattr(self,'unit_list',pd.read_csv(unit_path)['UNITS'].tolist())

	def reload_data(self):
		self.prod_df = pd.read_csv(self.product_path)

	def addnew_dict(self,new_dict):
		if ((not 'ID00' in new_dict.keys()) or new_dict['ID00']==''):
			print('KeyError')
			raise KeyError
			#raise Exception("Cannot make new product,\n No Product ID")
		if new_dict['ID00'] in self.prod_df['ID00'].tolist():
			raise IOError
			#raise Exception("Cannot make new product,\n Product ID exists")
		else:
			self.prod_df.loc[max(list(self.prod_df.index))+1] = new_dict

	def editex(self,new_dict):
		ind = list(self.prod_df[self.prod_df['ID00']==new_dict['ID00']].index)[0]
		self.prod_df.loc[ind] = new_dict

	def get_stock(self,id00,retclass=True):
		sh1 = stock_handle(id00,self.prod_df[self.prod_df['ID00']==id00]['STOCK'].iloc[0])
		if retclass:
			return sh1
		else:
			pass

	def query_data(self,id00):
		return self.prod_df[self.prod_df['ID00']==id00].iloc[0].to_dict()

	def update_stock(self,sth):
		sth.update_json()
		pid_ix = self.prod_df[self.prod_df['ID00']==sth.pid].iloc[0].name
		self.prod_df.at[pid_ix,'STOCK'] = sth.stock_json

	def save(self,path=None):
		if not path is None:
			self.prod_df.to_csv(path,index=False)
		else:
			self.prod_df.to_csv(self.product_path,index=False)

if __name__=="__main__":
	print('This script does nothing by itself')
