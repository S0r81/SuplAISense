import pdfplumber
import openai
import bson
import ast
from io import BytesIO

def parseDocumentPath(path,filename):# Replace this with your OpenAI API key
    openai.api_key = "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"
    pdf_file_path=path+filename
    pdf_text = extract_text_from_pdf_path(pdf_file_path)
    buyer_name = find_buyer_name_gpt(pdf_text)
    seller_name = find_seller_name_gpt(pdf_text)
    address = find_seller_address_gpt(pdf_text)
    products=find_products(pdf_text)
    date = find_date_gpt(pdf_text)
    pdf_binary = pdf_to_bson(pdf_file_path)
    return [filename,pdf_binary,seller_name,buyer_name,address,products,date]

def parseDocumentData(filename,file_content,binary):
    openai.api_key = "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"
    pdf_text = extract_text_from_pdf(file_content)
    buyer_name = find_buyer_name_gpt(pdf_text)
    seller_name = find_seller_name_gpt(pdf_text)
    address = find_seller_address_gpt(pdf_text)
    products=find_products(pdf_text)
    date = find_date_gpt(pdf_text)
    pdf_binary = binary
    return [filename,pdf_binary,seller_name,buyer_name,address,products,date]

def extract_text_from_pdf(pdf_data):
    pdf_data.headers['Content-Type'] = 'application/pdf'
    # Use pdfplumber to extract the text from the PDF
    with pdfplumber.open(BytesIO(pdf_data.data)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_pdf_path(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def find_buyer_name_gpt(text):
    prompt = f"The following text represents an invoice from a seller to a buyer. return the name of the buyer in the text below respond with the answer in one line and only the answer no explanation\n\n{text}\n"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_seller_name_gpt(text):
    prompt = f"The following text represents an invoice from a seller to a buyer. return the name of the seller in the text below respond with the answer in one line and only the answer no explanation\n\n{text}\n"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_seller_address_gpt(text):
    prompt = f"The following text represents an invoice from a seller to a buyer. return the address of the seller in the text below respond with the answer in one line and only the answer no explanation\n\n{text}\n"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_products(text):
    prompt = f'Based on the following invoice content, return an array of product name and quantity of product for each product in the transaction the format should be similar to [["Douglas Fir Home Frames", 20], ["Western Red Home Frames", 55], ["Hemlock Home Frames", 71]] do not include subtotal as a product. do not include total as a product, do not include tax as a product, do not include shipping as a product, return the answer and only the answer, no explanation.    \n\n{text}'
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )
    product_string = response.choices[0].text.strip()

    # Post-processing step to convert the response to a list of lists
    products = []
    for product in product_string.split("], ["):
        product = product.strip("[]")
        product_name, quantity = product.rsplit(",", 1)
        product_name = product_name.strip('"')
        
        # Check if the quantity is a valid integer
        try:
            quantity = int(quantity.strip())
        except ValueError:
            print(f"Invalid quantity value: {quantity}")
            continue

        products.append([product_name, quantity])

    return products


def find_date_gpt(text):
    prompt = f"Find the date of the invoice in the following text:\n\n{text}\nThe date is: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def pdf_to_bson(pdf_file_path):
    with open(pdf_file_path, "rb") as f:
        data = f.read()
    return bson.Binary(data)
