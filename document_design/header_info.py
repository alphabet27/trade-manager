import pylatex as tex

def make_header(doc,header_info={}):
	my_head = '''\\usepackage{array}
\\newcommand{\\PreserveBackslash}[1]{\\let\\temp=\\\\#1\\let\\\\=\\temp}
\\newcolumntype{C}[1]{>{\\PreserveBackslash\\centering}p{#1}}
\\newcolumntype{R}[1]{>{\\PreserveBackslash\\raggedleft}p{#1}}
\\newcolumntype{L}[1]{>{\\PreserveBackslash\\raggedright}p{#1}}'''
	# print(my_head)
	doc.preamble.append(tex.utils.NoEscape(my_head))
	doc.preamble.append(tex.utils.NoEscape('\\setlength{\\tabcolsep}{1mm}'))
	doc.preamble.append(tex.Command('usepackage','multirow'))
	doc.preamble.append(tex.utils.NoEscape('\\renewcommand*{\\familydefault}{\\ttdefault}'))
	company_name = 'Company Name'
	company_desc_line_1 = 'Your Company Description Line 1'
	company_desc_line_2 = 'Your Company Description Line 2'
	company_address = 'Your Company Address'
	company_contact_info = 'Your Company Phone Number and Email'
	document_invoice_type = 'Tax Invoice'
	# Appending to document
	title = tex.basic.HugeText(tex.position.Center(data=company_name))
	line_01 = tex.position.Center(data=company_desc_line_1)
	line_01.append(tex.LineBreak())
	line_01.append(company_desc_line_2)
	#line_01.append('Some More Text For testing')
	line_01.append(tex.LineBreak())
	line_01.append(company_address)
	line_01.append(tex.LineBreak())
	line_01.append(company_contact_info)
	line_01.append(tex.LineBreak())
	line_01.append(document_invoice_type)
	#
	doc.append(title)
	doc.append(tex.basic.LargeText(line_01))

if __name__=="__main__":
	gmt_options = {'top':'5mm','left':'5mm','right':'5mm'}
	doc = tex.Document(geometry_options = gmt_options)
	make_header(doc)
	doc.generate_tex(filepath='zz_sample_header')
	doc.generate_pdf(filepath='zz_sample_header',compiler='pdflatex')
