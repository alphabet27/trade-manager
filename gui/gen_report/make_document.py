from tkinter import messagebox
import webbrowser

from .table_fill import *
from .footer_info import make_footer

inv_cols = json.load(open("gen_report/invoice_table_cols.json",'r'))
invoice_info = json.load(open("gen_report/sample_invoice.json",'r'))
document_info = json.load(open('gen_report/document_data.json','r'))
table_colstyle = ''.join(open('gen_report/table_colstyle.tex','r').readlines())

class make_document(tex.Document):
	def __init__(self,document_info,show_cols=None):
		self.show_cols = show_cols
		self.document_info = document_info

		super().__init__(geometry_options = document_info['gmt_options'], page_numbers=False)
		self.preamble.append(tex.utils.NoEscape(table_colstyle))

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
		table1 = tex.Tabular(r"L{85mm} R{85mm}", width=2)
		table1.add_row(("GSTIN NO. " + self.document_info["GSTIN NO."],
						"DL. No. : " + self.document_info["Licence No."]))
		#table2 = tex.Tabular(r"L{85mm} R{85mm}", width=2)
		table1.add_row((f"STATE CODE : {self.document_info['STATE CODE']}", ""))
		line_02 = tex.position.Center(data="")
		line_02.append(table1)
		line_02.append(tex.LineBreak())
		line_02.append(self.document_info["document_invoice_type"])
		self.append(title)
		self.append(tex.basic.MediumText(line_01))
		self.append(tex.basic.LargeText(line_02))

	def make_invoice_table(self, invoice_info, footer_info, show_cols):
		table = make_tabular_inv(self, invoice_info)
		table = add_products(table, invoice_info["bill_df_ren"][list(show_cols.keys())], show_cols)
		make_footer(table, footer_info, document_info["company_name"])

	def save(self,filename,source=False,doc=True,compiler='pdflatex',opendoc=False):
		if source:
			self.generate_tex(filepath=filename)
			if opendoc:
				webbrowser.open_new_tab(filename+'.tex')
		if doc:
			self.generate_pdf(filepath=filename,compiler=compiler)
			if opendoc:
				webbrowser.open_new_tab(filename+'.pdf')
			else:
				messagebox.showinfo("Info", "Saved to "+filename)

def get_footer(doc_info, inv_table):
	taxes = []
	for tax in inv_table.GST.unique():
		temp = inv_table[inv_table['GST']==tax]
		taxes.append([tax,temp['TAXABLE'].sum(),(temp['TAXABLE']*tax/100).sum()])
	footer_info = {}
	footer_info.update(dict(Taxes=taxes,
						    TnC = doc_info["TnC"],
						    bank_info=doc_info["bank_info"]))
	return footer_info


class the_main:
	def execute(self, path=""):
		import pandas as pd
		df = pd.read_csv(f'{path}z_sample_prod_data.csv')
		sr1 = df["QTY"]*df["RATE"]*(1. + df["GST"]/100)
		sr1.name = "AMOUNT"
		df["AMOUNT"] = sr1.round(2)
		invoice_info["bill_df_ren"] = df
		# taxes = []
		# for tax in df.GST.unique():
		# 	temp = df[df['GST']==tax]
		# 	taxes.append([tax,temp['TAXABLE'].sum(),(temp['TAXABLE']*tax/100).sum()])
		# footer_info = json.load(open(f"{path}sample_invoice.json",'r'))
		footer_info = get_footer(document_info, df)
		# footer_info["Taxes"] = taxes
		# footer_info["TnC"] = document_info["TnC"]
		# footer_info["bank_info"] = document_info["bank_info"]
		d1 = make_document(document_info, show_cols = inv_cols)
		d1.make_header()
		d1.make_invoice_table(invoice_info, footer_info, inv_cols)
		d1.save('zz_sample_full',source=True,doc=False)

if __name__=="__main__":
	tm = the_main()
	tm.execute()
