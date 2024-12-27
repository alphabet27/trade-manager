import json
from table_fill import *

def num_to_words(num):
	fig_in_words = ''
	dig_to_word =  [[None,'','Ten',''],
					['','One','Eleven','Ten'],
					[None,'Two','Twelve','Twenty'],
					['Hundred','Three','Thirteen','Thirty'],
					['Thousand','Four','Fourteen','Forty'],
					[None,'Five','Fifteen','Fifty'],
					['Lakh','Six','Sixteen','Sixty'],
					[None,'Seven','Seventeen','Seventy'],
					['Crore','Eight','Eighteen','Eighty'],
					[None,'Nine','Nineteen','Ninety']]
	num_str = str(int(num))
	num_len = len(num_str)
	if num_len>9:
		print('Amount exceeding Rs.1,00,00,00,000 (Rs. 100 crore) word format not available')
		return ''
	elif num_len<10:
		pass

def make_footer(table,footer_info):
	r7_01 = tex.MultiRow(7,width='200pt',data='')
	r7_02 = tex.MultiRow(7,width='200pt',data='')
	amt_1 = footer_info["Taxable_05"]
	amt_2 = footer_info["Taxable_12"]
	amt_3 = footer_info["Taxable_18"]
	sub_table = tex.Tabular(r"|L{28mm} R{26mm} R{26mm} R{26mm}|",width=4)
	sub_table.add_hline()
	sub_table.add_row(("Tax Name", "Taxable", "CGST", "SGST"))
	sub_table.add_row(("GST 05%", round(amt_1,2), round(amt_1*0.025,2), round(amt_1*0.025,2)))
	sub_table.add_row(("GST 12%", round(amt_2,2), round(amt_2*0.06,2), round(amt_2*0.06,2)))
	sub_table.add_row(("GST 18%", round(amt_3,2), round(amt_3*0.09,2), round(amt_3*0.09,2)))
	sub_table.add_hline()
	r7_01.append(sub_table)

	c7_01 = tex.MultiColumn(7, align='|l', data=r7_01)
	c7_02 = tex.MultiColumn(7, align='|l', data="")
	c4_01 = tex.MultiColumn(4, align='|l|',data="Net. Amount")
	c4_02 = tex.MultiColumn(4, align='|l|',data="CGST")
	c4_03 = tex.MultiColumn(4, align='|l|',data="SGST")
	c4_04 = tex.MultiColumn(4, align='|l|',data="")
	c4_05 = tex.MultiColumn(4, align='|l|',data="Other Charges")
	c4_06 = tex.MultiColumn(4, align='|l|',data="Round Off")
	c4_07 = tex.MultiColumn(4, align='|l|',data=tex.basic.LargeText("Grand Total"))

	table.add_row((c7_01,c4_01,str(round(amt_1+amt_2+amt_3,2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_02,str(round((amt_1*0.025) + (amt_2*0.06) + (amt_3*0.09), 2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_03,str(round((amt_1*0.025) + (amt_2*0.06) + (amt_3*0.09), 2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_04,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_05,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_06,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_07,str(int((amt_1*1.05) + (amt_2*1.12) + (amt_3*1.18)))))
	table.add_hline()





if __name__=="__main__":
	df = pd.read_csv('z_sample_prod_data.csv')
	gmt_options = {'top':'5mm','left':'5mm','right':'5mm'}
	doc = tex.Document(geometry_options = gmt_options)
	customer_01 = json.load(open('sample_customer.json','r'))
	col_widths = json.load(open('col_widths.json','r'))
	invoice_info = json.load(open('sample_invoice.json','r'))
	footer_info = json.load(open('sample_footer.json','r'))
	doc.preamble.append(tex.Command('usepackage','multirow'))
	doc.preamble.append(tex.utils.NoEscape('\\renewcommand*{\\familydefault}{\\ttdefault}'))
	make_header(doc)
	table = make_tabular(doc,customer_01,invoice_info)
	add_products(table,df,col_widths)
	make_footer(table,footer_info)
	doc.generate_tex(filepath='zz_sample_full')
	doc.generate_pdf(filepath='zz_sample_full',compiler='pdflatex')

	#my_num = 13482
	#print(num_to_words(my_num))
