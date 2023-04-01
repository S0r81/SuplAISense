import PyPDF2
import re

def extract_attributes(pdf_file):
    # Open the PDF file in binary mode
    with open(pdf_file, 'rb') as f:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfFileReader(f)

        # Get the first page of the PDF
        page = pdf_reader.getPage(0)

        # Extract the text from the PDF
        text = page.extractText()

        # Use regular expressions to find the seller name, date, material description, buyer name, and location
        seller_name = re.search(r'Seller:\s*(.*)\s*Date', text).group(1)
        date = re.search(r'Date:\s*(.*)\s*Material', text).group(1)
        material_desc = re.search(r'Material Description:\s*(.*)\s*Buyer', text).group(1)
        buyer_name = re.search(r'Buyer:\s*(.*)\s*Location', text).group(1)
        location = re.search(r'Location:\s*(.*)\s*Amount', text).group(1)

        # Return the extracted information as a tuple of strings
        return seller_name.strip(), date.strip(), material_desc.strip(), buyer_name.strip(), location.strip()
