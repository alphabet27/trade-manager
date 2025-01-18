import json
import webbrowser
import pandas as pd
import pylatex as tex


from table_fill import add_products
from table_info import make_tabular_inv
from footer_info import make_footer

db_path = '../scripts/sample_database/'
database = json.load(open(db_path + 'database.json','r'))
for db_table, tab_path in database.items():
	database[db_table] = db_path + tab_path

document_info = json.load(open(database['document_data'],'r'))
table_colstyle = ''.join(open(db_path + 'table_colstyle.tex','r').readlines())
show_cols = None
#show_cols = json.load(open('col_widths.json','r'))

class make_document:
	def __init__(self,document_info,show_cols=show_cols):
		self.show_cols = show_cols
		self.document_info = document_info

		self.doc = tex.Document(geometry_options = document_info['gmt_options'], page_numbers=False)
		self.doc.preamble.append(tex.utils.NoEscape(table_colstyle))

	def make_header(self):
		title = tex.basic.HugeText(tex.position.Center(data=self.document_info["company_name"]))
		line_01 = tex.position.Center(data=self.document_info["company_desc_line_1"])
		line_01.append(tex.LineBreak())
		line_01.append(self.document_info["company_desc_line_2"])
		line_01.append(tex.LineBreak())
		line_01.append(self.document_info["company_address"])
		line_01.append(tex.LineBreak())
		line_01.append(self.document_info["company_contact_info"])
		line_01.append(tex.LineBreak())
		line_01.append(self.document_info["document_invoice_type"])
		#
		self.doc.append(title)
		self.doc.append(tex.basic.LargeText(line_01))

	def make_invoice_table(self,invoice_info, footer_info,show_cols):
		table = make_tabular_inv(self.doc, invoice_info)
		table = add_products(table, invoice_info["bill_df_ren"][list(show_cols.keys())], show_cols)
		make_footer(table, footer_info, document_info["company_name"])


	def save(self,filename,source=False,doc=True,compiler='pdflatex',opendoc=False):
		if source:
			self.doc.generate_tex(filepath=filename)
			if opendoc:
				webbrowser.open_new_tab(filename+'.tex')
		if doc:
			self.doc.generate_pdf(filepath=filename,compiler=compiler)
			if opendoc:
				webbrowser.open_new_tab(filename+'.pdf')
		else:
			raise Exception("Saved to "+filename)

if __name__=="__main__":
	invoice_info = json.load(open("sample_invoice.json",'r'))
	df = pd.read_csv('z_sample_prod_data.csv')
	sr1 = df["QTY"]*df["RATE"]*(1. + df["GST"]/100)
	sr1.name = "AMOUNT"
	#print(sr1)
	df["AMOUNT"] = sr1.round(2)
	#print(df)
	invoice_info["bill_df_ren"] = df
	taxes = []
	for tax in df.GST.unique():
		temp = df[df['GST']==tax]
		taxes.append([tax,temp['TAXABLE'].sum(),(temp['TAXABLE']*tax/100).sum()])
	footer_info = json.load(open("sample_invoice.json",'r'))
	footer_info["Taxes"] = taxes
	show_cols = json.load(open("invoice_table_cols.json",'r'))
	d1 = make_document(document_info, show_cols = show_cols)
	d1.make_header()
	d1.make_invoice_table(invoice_info, footer_info, show_cols)
	d1.save('zz_sample_full',source=True,doc=False)
