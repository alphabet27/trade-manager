import pandas as pd
	
class manage_party:
	def __init__(self,path='sample_database/party_list',df_party=None):
		self.path = path
		if type(df_party)!=type(None):
			self.df_party = df_party
		else:
			self.df_party = pd.read_csv(path)
			
	def reload(self):
		self.df_party = pd.read_csv(path)
		
	def get_index(self,new_dict):
		if not 'ALIAS0' in list(new_dict.keys()):
			return None
		elif not new_dict['ALIAS0'] in self.df_party['ALIAS0'].tolist():
			return None
		else:
			return self.df_party[self.df_party['ALIAS0']==new_dict['ALIAS0']].iloc[0].name
		
	def addnew(self,alias,party_name,address,contact,party_type):
		new_row =[alias,party_name,address,contact,party_type]
		self.df_party.loc[len(self.df_party)] = new_row
		
	def addnew_dict(self,new_dict):
		self.df_party.loc[max(self.df_party.index)+1] = new_dict
	
	def edit_by_dict(self,new_dict):
		ind = self.get_index(new_dict)
		print(ind)
		if ind:
			del new_dict['ALIAS0']
			self.df_party.loc[ind,new_dict.keys()] = new_dict.values()
		else:
			raise Exception('Product Entry Not Found')
	
	def editex(self,ind,party_name=None,address=None,contact=None,party_type=None):
		old_row = self.df_party.iloc[ind].tolist()
		new_row = [old_row[0],party_name,address,contact,party_type]
		columns = self.df_party.columns
		for i in range(len(new_row)):
			if new_row[i]==None:
				new_row[i] = old_row[i]
			else:
				pass
		for col in range(len(columns)):
			self.df_party.at[ind,columns[col]] = new_row[col]
		
	def save(self,path=None,index=False):
		if type(path)!=type('a'):
			path = self.path
		self.df_party.to_csv(path,index=index)
		
if __name__=="__main__":
	print("This script does nothing by itself")

