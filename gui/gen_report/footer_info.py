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

def justify_float(num):
	#print(num)
	new_num = str(float(num)).split(".")
	new_num[1].ljust(2,'0')
	return ".".join(new_num)

def make_footer(table,footer_info,company_name):
	r7_01 = tex.MultiRow(7,width='200pt',data='')
	r7_02 = tex.MultiRow(7,width='200pt',data='')
	r5_01 = tex.MultiRow(5,width='150pt',data='')
	r5_02 = tex.MultiRow(5,width='120pt',data='')
	r5_03 = tex.MultiRow(5,width='200pt',data='')
	sub_table = tex.Tabular(r"|L{28mm} R{26mm} R{26mm} R{26mm}|",width=4)
	sub_table.add_hline()
	sub_table.add_row(("Tax Name", "Taxable", "CGST", "SGST"))
	net_taxation = {"taxable":0,"tax":0}
	for tax_name, taxable, tax in footer_info["Taxes"]:
		sub_table.add_row(("GST " + str(round(tax_name,2)).rjust(2,'0') + "%", justify_float(taxable), justify_float(tax), justify_float(tax)))
		net_taxation["tax"]+=tax
		net_taxation["taxable"]+=taxable
	sub_table.add_hline()
	r7_01.append(sub_table)

	for i in range(len(footer_info["TnC"])):
		if not i==0:
			r5_01.append(tex.LineBreak())
		r5_01.append(footer_info["TnC"][i])

	for key, val in footer_info["bank_info"].items():
		if not key=='Bank':
			r5_02.append(tex.LineBreak())
		r5_02.append(key+' : '+str(val))

	line2 = tex.position.FlushRight(data="For "+company_name)
	line2.append(tex.LineBreak())
	line2.append(tex.LineBreak())
	#line2.append(tex.LineBreak())
	line2.append("Authorised Signatory")

	r5_03.append(tex.basic.LargeText(line2))

	c7_01 = tex.MultiColumn(7, align='|l', data=r7_01)
	c7_02 = tex.MultiColumn(7, align='|l', data="")
	c4_01 = tex.MultiColumn(4, align='|l|',data="Net. Amount")
	c4_02 = tex.MultiColumn(4, align='|l|',data="CGST")
	c4_03 = tex.MultiColumn(4, align='|l|',data="SGST")
	c4_04 = tex.MultiColumn(4, align='|l|',data="")
	c4_05 = tex.MultiColumn(4, align='|l|',data="Other Charges")
	c4_06 = tex.MultiColumn(4, align='|l|',data="Round Off")
	c4_07 = tex.MultiColumn(4, align='|l|',data=tex.basic.LargeText("Grand Total"))

	c3_08 = tex.MultiColumn(3, align='|l|', data = r5_01)
	c3_09 = tex.MultiColumn(3, align='|l|', data = '')
	c4_09 = tex.MultiColumn(4, align='|l|', data = r5_02)
	c4_10 = tex.MultiColumn(4, align='|l|', data = '')
	c5_11 = tex.MultiColumn(5, align='|l|', data = r5_03)
	c5_12 = tex.MultiColumn(5, align='|l|', data = '')

	table.add_row((c7_01,c4_01,str(round(net_taxation["taxable"],2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_02,str(round(net_taxation["tax"], 2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_03,str(round(net_taxation["tax"], 2))))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_04,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_05,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_06,""))
	table.add_hline(8,12)
	table.add_row((c7_02,c4_07,str(int(net_taxation["taxable"] + net_taxation["tax"]))))
	table.add_hline()
	table.add_row((c3_08,c4_09,c5_11))
	table.add_row((c3_09,c4_10,c5_12))
	table.add_row((c3_09,c4_10,c5_12))
	table.add_row((c3_09,c4_10,c5_12))
	table.add_row((c3_09,c4_10,c5_12))
	table.add_row((c3_09,c4_10,c5_12))
	table.add_hline()





if __name__=="__main__":
	df = pd.read_csv('z_sample_prod_data.csv')
	gmt_options = {'top':'5mm','left':'5mm','right':'5mm'}
	doc = tex.Document(geometry_options = gmt_options, page_numbers=False)
	#customer_01 = json.load(open('sample_customer.json','r'))
	col_widths = json.load(open('invoice_table_cols.json','r'))
	invoice_info = json.load(open('sample_invoice.json','r'))
	footer_info = json.load(open('sample_footer.json','r'))
	doc.preamble.append(tex.Command('usepackage','multirow'))
	doc.preamble.append(tex.utils.NoEscape('\\renewcommand*{\\familydefault}{\\ttdefault}'))
	make_header(doc)
	table = make_tabular_inv(doc,invoice_info)
	add_products(table,df,col_widths)
	make_footer(table,footer_info)
	doc.generate_tex(filepath='zz_sample_full')
	#doc.generate_pdf(filepath='zz_sample_full',compiler='pdflatex')

	#my_num = 13482
	#print(num_to_words(my_num))
