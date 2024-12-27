import json
import pandas as pd
import pylatex as tex
from table_info import make_tabular_inv
from header_info import make_header

def line_endings(fill_line,tab_width=10,char_width=1):
	fill_list = str(fill_line).split(' ')
	occ_width = 0
	nlines = 1
	for word in fill_list:
		if len(word)>tab_width:
			#print('Too long word. May overfill')
			pass
		elif occ_width+len(word)>tab_width:
			nlines+=1
			occ_width = len(word) + 1
		else:
			occ_width += len(word) + 1
	return nlines

def add_products(table,rendered_prod_df,col_widths,max_lines=20,carry_over=False):
	curr_line = 1
	i = 0
	while i in range(len(rendered_prod_df)):
		prod_data = rendered_prod_df.iloc[i].to_dict()
		row_data = tuple(prod_data.values())
		table.add_row(row_data)
		nlines = 1
		for key,value in prod_data.items():
			nlines = max([nlines,line_endings(value,tab_width=col_widths[key])])
		curr_line+=nlines
		if curr_line>max_lines:
			print('Reached end of table')
			carry_over = True
			break
		i+=1
	if curr_line>=max_lines:
		pass
	else:
		for i in range(max_lines-curr_line):
			table.add_row(("","","","","","","","","","","",""))
	table.add_hline()
	print('Table filled with',int(carry_over),'carry over pages')
	print('Occupied lines',curr_line-1)
	return table

if __name__=='__main__':
	df = pd.read_csv('z_sample_prod_data.csv')
	gmt_options = {'top':'5mm','left':'5mm','right':'5mm'}
	doc = tex.Document(geometry_options = gmt_options)
	customer_01 = json.load(open('sample_customer.json','r'))
	col_widths = json.load(open('col_widths.json','r'))
	invoice_info = json.load(open('sample_invoice.json','r'))
	doc.preamble.append(tex.Command('usepackage','multirow'))
	doc.preamble.append(tex.utils.NoEscape('\\renewcommand*{\\familydefault}{\\ttdefault}'))
	make_header(doc)
	table = make_tabular(doc,customer_01,invoice_info)
	add_products(table,df,col_widths)
	doc.generate_tex(filepath='zz_sample_full')

