import json
import webbrowser
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

class make_document:
	def __init__(self,document_info):
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

	def make_invoice_table(self,invoice_info):
		table = make_tabular_inv(self.doc, self.invoice_info["customer_info"], self.invoice_info["subdata"])
		col_widths = [10]*12
		table = add_products(self.table, invoice_info["bill_df_ren"], col_widths)
		make_footer(table, invoice_info)


	def save(self,filename,compiler='pdflatex'):
		self.doc.generate_pdf(filepath=filename,compiler=compiler)

if __name__=="__main__":
	d1 = make_document(document_info)
	d1.make_header()
	d1.save('zz_sample_full')
