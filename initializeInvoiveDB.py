
#for each file in the invoice directory extract the information using static/DocumentExtract2.py and save it to the mongodb database
for file in os.listdir(invoice_dir):
    attributes=DocumentExtract2.extract_text_from_pdf(invoice_dir+file)
    