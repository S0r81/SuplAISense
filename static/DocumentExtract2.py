import pdfplumber
import openai
import re
def main():
    # modify this to extract bson binary of the pdf, seller name, buyer name, address, description, quantity and date and return these in an array
    # Replace this with your OpenAI API key
    openai.api_key = "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"

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def find_customer_name_gpt(text):
    prompt = f"Find the customer name in the following text:\n\n{text}\nThe customer name is: "
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

pdf_file_path = 'path/to/your/pdf/file.pdf'
pdf_text = extract_text_from_pdf(pdf_file_path)
customer_name = find_customer_name_gpt(pdf_text)

if customer_name:
    print("Customer name found:", customer_name)
else:
    print("Customer name not found.")
