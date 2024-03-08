import pandas as pd

''' 
	Test the edit_transactions functions
	How to add/subtract stock on every sale/purchase transaction?
	
'''

party_path = '../scripts/sample_database/party_list.csv'
stock_path = '../scripts/sample_database/stock_list.csv'
product_path = '../scripts/sample_database/product_list.csv'
billdata_path = '../scripts/sample_database/sale_billdata.csv'
transactions_path = '../scripts/sample_database/sale_data.csv'

class transactions:
	def __init__(self,party_path,billdata_path,transactions_path):
		self.no_loadings = 0
		self.party_path = party_path
		self.billdata_path = billdata_path
		self.transactions_path = transactions_path
		self.party_map = pd.read_csv(party_path, usecols=['ALIAS0','PARTY0'])
		self.df_billdata = pd.read_csv(billdata_path)
		self.df_transaction = pd.read_csv(transactions_path)
	
	def get_amount(self,billno):
		new_df = self.df_transaction[self.df_transaction['BILL0']==billno]
		return (new_df.QTY * new_df.RATE).sum()
		
	def get_party(self,alias):
		return self.party_map[self.party_map['ALIAS0']==alias]['PARTY0'].to_list()[0]

	def full_data(self):
		df_full = pd.DataFrame(columns=['BILL0','DATE0','PARTY','Narration','Net Amount'])
		i=0
		new_row = {}
		while i < len(self.df_billdata):
			for column in self.df_billdata.columns:
				new_row[column] = self.df_billdata.iloc[i][column]
			new_row['Net Amount'] = self.get_amount(new_row['BILL0'])
			new_row['PARTY'] = self.get_party(new_row['ALIAS0'])
			df_full.loc[len(df_full)] = new_row
			i+=1
		self.no_loadings += 1
		return df_full
		
	def billdata(self,billno):
		if not billno==0:
			df_bill = self.df_transaction[self.df_transaction['BILL0']==billno]
			self.df_bill = df_bill.drop(df_bill.columns[0],axis=1)
			temp = self.df_billdata[self.df_billdata['BILL0']==billno].index
			if len(temp)>0:
				self.curr_billdata = self.df_billdata.iloc[temp[0]].to_dict()
				self.curr_billdata['PARTY0'] = self.get_party(self.curr_billdata['ALIAS0'])
				print('Current Bill -\n',self.curr_billdata)
			else:
				self.curr_billdata = None
				print('No bill found')
		else:
			df_bill = pd.DataFrame(columns=self.df_transaction.columns)
			self.df_bill = df_bill.drop(df_bill.columns[0],axis=1)
			self.curr_billdata = {'BILL0':billno, 'DATE0':None, 'ALIAS0':None}
		
	def add_transactions(self,billno,df_entries,**kwargs):
		ext = max(list(self.df_transactions.index))
		for i in range(len(df_entries)):
			temp = df_entries.loc[i].to_dict()
			temp['BILL0'] = billno
			self.df_transactions.loc[ext+i+1] = temp
		print('Added')
	
	def edit_transactions(self,billno,df_editables=None,**kwargs):
		if type(df_editables)==type(None):
			df_editables = self.df_bill
		indices = list(df_editables.index)
		for i in indices:
			self.df_transaction.drop(i,inplace=True)
		self.df_transaction.reset_index(inplace=True,drop=True)
		indices = list(df_editables.index)
		for j in indices:
			l = len(self.df_transaction)
			self.df_transaction.loc[l] = df_editables.iloc[j].to_dict()
		self.df_transaction.sort_values(by=['BILL0','REF_NO'], inplace=True, ascending=[True,True])
		
	def save(self,what):
		if not what.lower() in ['billdata','transactions','both']:
			print('Invalid save option!')
		elif what.lower()=='billdata':
			self.df_billdata.to_csv(self.billdata_path,index=False)
		elif what.lower()=='transactions':
			self.df_transactions.to_csv(self.transactions_path,index=False)


if __name__=='__main__':
	party_map = pd.read_csv('sample_database/party_list.csv', usecols=['ALIAS0','PARTY0'])
	df_billdata = pd.read_csv('sample_database/sale_billdata.csv')
	df_transaction = pd.read_csv('sample_database/sale_fulldata.csv')
	
	print(transactions(party_map,df_billdata,df_transaction).full_data())

