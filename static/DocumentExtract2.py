import pdfplumber
import openai
import bson

def parseDocument(pdf_file_path):# Replace this with your OpenAI API key
    openai.api_key = "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"
    pdf_text = extract_text_from_pdf(pdf_file_path)
    buyer_name = find_buyer_name_gpt(pdf_text)
    seller_name = find_seller_name_gpt(pdf_text)
    address = find_address_gpt(pdf_text)
    products=[]
    descriptions = find_product_description_gpt(pdf_text)
    for description in descriptions:
        quantity = find_quantity_gpt(description,pdf_text)
        products.append([description,quantity])
    date = find_date_gpt(pdf_text)
    pdf_binary = pdf_to_bson(pdf_file_path)
    return [pdf_binary,seller_name,buyer_name,address,products,date]

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def find_buyer_name_gpt(text):
    prompt = f"Find the buyer name in the following text:\n\n{text}\nThe customer name is: "
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
    prompt = f"Find the seller name in the following text:\n\n{text}\nThe seller name is: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_address_gpt(text):
    prompt = f"Find the address of the seller in the following text:\n\n{text}\nThe address is: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_product_description_gpt(text):
    prompt = f"Find all the descriptions of the products and write them as a comma seperated list of the descriptions from the following text :\n\n{text}\nThe descriptions: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def find_quantity_gpt(descripotion,text):
    prompt = f"Find the quantity of {descripotion} in the following text:\n\n{text}\nThe quantity is: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

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
