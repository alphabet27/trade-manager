import pandas as pd

def check_anonymous(stock_string):
	stock_list = stock_string.split('\\;')
	i = 0
	while stock_list[i] in stock_list:
		if '\\' in stock_list[i]:
			return True
		i+=1
	return False

def stock_reader(stock_string):
	if check_anonymous(stock_string):
		raise Exception('Backslash "\\" in batch number not allowed. Use forward slash "/" instead.')
	stock_list = stock_string.split(';')
	i = 0
	removable = []
	while stock_list[i] in stock_list:
		if '\\' in stock_list[i] and i<len(stock_list):
			stock_list[i] = stock_list[i] + stock_list[i+1]
			removable.append(i+1)
		i+=1
	for j in range(len(removable)):
		del stock_list[removable[j]]
	return stock_list
	

