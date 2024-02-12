import pandas as pd

def addnew(df,billno,pid,qty,rate,batch,exp):
	new_row =[7,"id08",10,120,"batch08","exp08"]
	df.loc[len(df)] = new_row
	return df
	
def editex(df,ind,pid=None,qty=None,rate=None,batch=None,exp=None):
	old_row = df.iloc[ind].tolist()
	new_row = [old_row[0],pid,qty,rate,batch,exp]
	columns = df.columns
	for i in range(6):
		if new_row[i]==None:
			new_row[i] = old_row[i]
		else:
			pass
	for col in range(len(columns)):
		df.at[ind,columns[col]] = new_row[col]
	return df


if __name__=="__main__":
	print("This script does nothing by itself")

