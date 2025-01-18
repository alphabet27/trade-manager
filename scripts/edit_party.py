import pandas as pd
	
class manage_party:
	def __init__(self,database):
		self.path = database['party_path']
		self.df_party = pd.read_csv(self.path)

	def reload_data(self):
		self.df_party = pd.read_csv(self.path)
		
	def get_index(self,new_dict):
		if not 'ALIAS0' in list(new_dict.keys()):
			return None
		elif not new_dict['ALIAS0'] in self.df_party['ALIAS0'].tolist():
			return None
		else:
			return self.df_party[self.df_party['ALIAS0']==new_dict['ALIAS0']].iloc[0].name
		
	def addnew_dict(self,new_dict):
		self.df_party.loc[max(self.df_party.index)+1] = new_dict
	
	def edit_by_dict(self,new_dict):
		ind = self.get_index(new_dict)
		print(ind)
		if ind:
			del new_dict['ALIAS0']
			self.df_party.loc[ind,new_dict.keys()] = new_dict.values()
		else:
			raise Exception('Party Entry Not Found')
		
	def save(self,path=None,index=False):
		if path is None:
			path = self.path
		self.df_party.to_csv(path,index=index)
		
if __name__=="__main__":
	print("This script does nothing by itself")

