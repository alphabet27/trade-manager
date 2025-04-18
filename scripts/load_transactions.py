import pandas as pd

database = {"party_path" : '../scripts/sample_database/party_list.csv',
			"product_path" : '../scripts/sample_database/product_list.csv',
			"billdata_path" : '../scripts/sample_database/sale_billdata.csv',
			"transactions_path" : '../scripts/sample_database/sale_fulldata.csv'}

db_path = 'scripts/sample_database/'
db_addr = {"fulldata" : {"fy1":'fulldata_fy1.csv',
					 "fy2":'fulldata_fy1.csv'}}


'''		Make database loader in the following format
class loader_2:
	def __init__(self,db_path, db_addr, fy,prod_man=None,mode='sale'):
		self.full_dpath = db_path + db_addr[fy]
'''

class transactions:
	def __init__(self,database,prod_man=None,mode='sale'):
		self.mode = mode		# Will be used soon
		self.no_loadings = 0
		self.party_path = database['party_path']
		self.product_path = database['product_path']
		self.billdata_path = database['billdata_path']
		self.transactions_path = database['transactions_path']
		self.party_map = pd.read_csv(self.party_path, usecols=['ALIAS0','PARTY0'])
		self.df_billdata = pd.read_csv(self.billdata_path)
		self.df_transaction = pd.read_csv(self.transactions_path)
		if not prod_man is None:
			self.prod_man = prod_man
			self.product_map = prod_man.prod_df
		else:
			self.product_map = pd.read_csv(self.product_path, usecols=['ID00','PRODUCT0','GST'])

	def get_amount(self,billno):
		new_df = self.df_transaction[self.df_transaction['BILL0']==billno]
		sr1 = (new_df.QTY * (new_df.RATE*(1 - new_df.DISC/100))).reset_index(drop=True)
		sr1.name = 'TAXABLE'
		return sr1

	def get_party_data(self,alias,get_full=False):
		if get_full:
			party_map = pd.read_csv(database["party_path"])
			return party_map[party_map['ALIAS0']==alias].iloc[0].to_dict()
		else:
			return self.party_map[self.party_map['ALIAS0']==alias].iloc[0].to_dict()

	def full_data(self):
		df_full = pd.DataFrame(columns=['BILL0','DATE0','PARTY','Narration','Net Amount'])
		i=0
		new_row = {}
		while i < len(self.df_billdata):
			new_row.update(self.df_billdata.iloc[i].to_dict())
			new_row['Net Amount'] = self.get_amount(new_row['BILL0']).sum()
			new_row['PARTY'] = self.get_party_data(new_row['ALIAS0'])['PARTY0']
			df_full.loc[len(df_full)] = new_row
			i+=1
		self.no_loadings += 1
		self.df_full = df_full

	def billdata(self,billno):
		if not billno==0:
			df_bill = self.df_transaction[self.df_transaction['BILL0'] == billno]
			self.df_bill = (df_bill.drop(df_bill.columns[0],axis=1).merge(self.product_map[['ID00','PRODUCT0','HSN']]))[['REF_NO','ID00','PRODUCT0','HSN','QTY','RATE','MRP','GST','DISC','BATCH00','EXP00']] #,'TAXABLE']]
			#print("df_bill =",self.df_bill)
			self.df_bill = self.df_bill.merge(self.get_amount(billno),left_index=True,right_index=True)
			temp = self.df_billdata[self.df_billdata['BILL0']==billno].index
			if len(temp)>0:
				self.curr_billdata = self.df_billdata.iloc[temp[0]].to_dict()
				self.curr_billdata['PARTY0'] = self.get_party_data(self.curr_billdata['ALIAS0'])['PARTY0']
				print('Current Bill -\n',self.curr_billdata)
			else:
				self.curr_billdata = None
				print('No bill found')
		else:
			df_bill = pd.DataFrame(columns=list(self.df_transaction.columns)+['PRODUCT0','HSN','TAXABLE'])
			self.df_bill = df_bill.drop(df_bill.columns[0],axis=1)[['REF_NO','ID00','PRODUCT0','HSN','QTY','RATE','MRP','GST','DISC','BATCH00','EXP00','TAXABLE']]
			self.curr_billdata = None

	def add_transactions(self,billno,billdata,df_entries=None,**kwargs):
		if billno in self.df_billdata['BILL0'].tolist():
			raise Exception(str(billno)+" exists")
		print("No error, proceeding")
		if df_entries is None:
			df_entries = self.df_bill
		ext = max(list(self.df_transaction.index))
		for i in range(len(df_entries)):
			temp = df_entries.iloc[i].to_dict()
			temp['BILL0'] = billno
			self.df_transaction.loc[ext+i+1] = temp
		self.df_billdata.reset_index(inplace=True,drop=True)
		billdata.update({"BILL0":billno})
		self.df_billdata.loc[len(self.df_billdata)] = billdata
		print("Adding billdata",billdata)
		print("Last 5 bills",self.df_billdata.tail(5))
		print('Added')

	def edit_transactions(self,billno=None,billdata={},df_editables=None,**kwargs):
		self.curr_billdata.update(billdata)
		if billno is None:
			billno = self.curr_billdata['BILL0']
		if df_editables is None:
			df_editables = self.df_bill
		for i in list(self.df_transaction[self.df_transaction['BILL0']==billno].index):
			self.df_transaction.drop(i,inplace=True)
		self.df_transaction.reset_index(inplace=True,drop=True)
		for j in list(df_editables.index):
			l = len(self.df_transaction)
			self.df_transaction.loc[l] = df_editables.iloc[j].to_dict()
			self.df_transaction.at[l,'BILL0'] = billno
		self.df_transaction.sort_values(by=['BILL0','REF_NO'], inplace=True, ascending=[True,True])
		nb = self.df_billdata[self.df_billdata['BILL0']==billno].iloc[0].name
		self.df_billdata.loc[nb] = self.curr_billdata

	def save(self,bill_info=True,full_transactions=True):
		self.df_billdata["BILL0"] = pd.to_numeric(self.df_billdata["BILL0"])
		self.df_transaction["BILL0"] = pd.to_numeric(self.df_transaction["BILL0"])
		self.df_transaction["REF_NO"] = pd.to_numeric(self.df_transaction["REF_NO"])
		self.df_billdata.sort_values('BILL0',inplace=True)
		self.df_transaction.sort_values(["BILL0","REF_NO"],inplace=True)
		if bill_info:
			self.df_billdata.to_csv(self.billdata_path,index=False)
		if full_transactions:
			self.df_transaction.to_csv(self.transactions_path,index=False)

if __name__=='__main__':
	print(transactions(database).full_data())
