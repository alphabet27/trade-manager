import json
import pylatex as tex
from header_info import make_header

def make_tabular_inv(doc,invoice_info):
	customer_info = invoice_info["customer_info"]
	table = tex.Tabular(r"|R{6mm}|L{41mm}|p{11mm}|p{10mm}|p{15mm}|p{14mm}|p{9mm}|p{14mm}|p{15mm}|p{12mm}|p{10mm}|R{23mm}|",width=12)	#Not adding the width gives error as R{},L{},C{} are not standard LaTeX tabular specs.
	table.add_hline()
	r8_01 = tex.MultiRow(8,width='200pt',data='')
	r8_02 = tex.MultiRow(8,width='200pt',data='')
	r2_01 = tex.MultiRow(2,width='200pt',data='')
	r2_02 = tex.MultiRow(2,width='200pt',data='')
	r2_03 = tex.MultiRow(2,width='200pt',data='')
	r2_04 = tex.MultiRow(2,width='200pt',data='')
	for key,value in customer_info.items():
		if not (key=='NAME0' or key=='ALIAS0'):
			r8_01.append(tex.LineBreak())
			r8_01.append(value)
		elif key=='NAME0':
			r8_01.append(value)
		else:
			pass
	r2_01.append('Inv_No : ' + str(invoice_info['BILL0']))
	r2_01.append(tex.LineBreak())
	r2_01.append('Inv_Dt : ' + str(invoice_info['DATE0']))
	#
	r2_02.append('Chl_No : ' + str(invoice_info['CHL. No.']))
	r2_02.append(tex.LineBreak())
	r2_02.append('Chl_Dt : ' + str(invoice_info['CHL. Dt.']))
	#
	r2_03.append('') #invoice_info['TDS_No'])
	r2_03.append(tex.LineBreak())
	r2_03.append('') #invoice_info['LR_Num'])
	r2_03.append(tex.LineBreak())
	r2_03.append('CHQ. No.') #invoice_info['Chq_No'])
	#
	c7_01 = tex.MultiColumn(7, align='|l',data=r8_01)
	c7_02 = tex.MultiColumn(7, align='|l',data=r8_02)
	c5_01 = tex.MultiColumn(5, align='|l|',data=r2_01)
	c5_02 = tex.MultiColumn(5, align='|l|',data=r2_02)
	c5_03 = tex.MultiColumn(5, align='|l|',data=r2_03)
	c5_04 = tex.MultiColumn(5, align='|l|',data=r2_04)
	#
	table.add_row((c7_01,c5_01))
	table.add_row((c7_02,c5_04))
	table.add_hline(8,12)
	table.add_row((c7_02,c5_02))
	table.add_row((c7_02,c5_04))
	table.add_hline(8,12)
	table.add_row((c7_02,c5_03))
	table.add_row((c7_02,c5_04))
	table.add_row((c7_02,c5_04))
	table.add_row((c7_02,c5_04))
	table.add_hline()
	#Add table to doc
	doc.append(tex.position.Center(data=table))
	return table


if __name__=='__main__':
	gmt_options = {'top':'5mm','left':'5mm','right':'5mm'}
	doc = tex.Document(geometry_options = gmt_options)
	invoice_info = json.load(open("sample_invoice.json",'r'))
	#doc.preamble.append(tex.Command('setmainfont','Latin Modern Mono',options='Ligatures=TeX'))
	make_header(doc)
	table = make_tabular_inv(doc,invoice_info)
	doc.generate_tex(filepath='zz_sample_full')
