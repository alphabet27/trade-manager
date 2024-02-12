import pandas as pd

class manage_prod:
	def __init__(self, prod_path='sample_database/product_list.csv', stock_path='sample_database/stock_list.csv'):
		self.prod_path = prod_path
		self.stock_path = stock_path
		self.prod_df = pd.read_csv(prod_path)
		self.stock_df = pd.read_csv(stock_path)
		
	def reload(self):
		self.prod_df = pd.read_csv(self.prod_path)
		self.stock_df = pd.read_csv(self.stock_path)

	def addnew(self,id00,prod_name,gst,unit,hsn=None):
		new_row =[id00,prod_name,gst,unit,hsn]
		self.prod_df.loc[len(self.prod_df)] = new_row
		
	def editex(self,ind,prod_name=None,unit=None,gst=None,hsn=None):
		old_row = self.prod_df.iloc[ind].tolist()
		new_row = [old_row[0],prod_name,unit,gst,hsn]
		columns = self.prod_df.columns
		for i in range(len(new_row)):
			if new_row[i]==None:
				new_row[i] = old_row[i]
			else:
				pass
		for col in range(len(columns)):
			self.prod_df.at[ind,columns[col]] = new_row[col]
	
	def get_stock(self,id00):
		return (self.stock_df[self.stock_df['ID00']==id00].iloc[0]['STOCK']).split(';')
			
	def add_stock(self,id00,new_stock):
		l1 = self.get_stock(id00)
		if len(l1)>0:
			self.stock_df.loc[len(self.stock_df)] = {'ID00':id00,'STOCK':';'.join(l1) + new_stock}
		else:
			self.stock_df.loc[len(self.stock_df)] = {'ID00':id00,'STOCK':new_stock}
			
	def edit_stock(self,id00,new_stock,ind=None):
		record = self.stock_df[self.stock_df['ID00']==id00].index
		if len(record)<1:
			print('No stock available, try adding stock instead!')
		elif len(record)>1:
			print('Unexpected double records found')
		else:
			index = record[0]
			self.stock_df.at[index,'STOCK'] = new_stock
			
	def save(self,what='prod',path=None):
		if what=='prod':
			if type(path)!=type('a'):
				path = self.prod_path
			self.prod_df.to_csv(path,index=False)
		elif what=='stock':
			if type(path)!=type('a'):
				path = self.stock_path
			self.stock_df.to_csv(path,delimiter=',',index=False)
	
if __name__=="__main__":
	print("This script does nothing by itself")

