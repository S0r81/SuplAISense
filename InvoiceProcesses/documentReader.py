from pymongo import MongoClient
from . import DocumentExtract2
from flask import make_response, session
def parse_temp_file(filename):
    client = MongoClient(
        "mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    temp_invoice_db = client.temp_invoices.temp_invoices
    invoice_db = client.user_invoices.user_invoices
    users_db = client.user_login_system.users
    file=temp_invoice_db.find_one({'filename':filename})
    # temp_invoice_db.delete_one({'filename':filename})
    file_content= make_response(file["content"])
    if file['filename'][-4:] == ".pdf":
        attributes = DocumentExtract2.parseDocumentData(file['filename'],file_content,file["content"])
        # Find user by session
        buyer = users_db.find_one({"name": attributes[3]})
        if buyer:
            buyer_id = buyer["_id"]
        else:
            buyer_id = session['user']['_id']
            print(f"User not found for buyer_name: {attributes[3]}")
        # Save the invoice in the user_invoices collection with the user_id reference
        invoice_db.insert_one({
            'filename': attributes[0],
            'pdf_binary': attributes[1],
            'seller_name': attributes[2],
            'buyer_name': attributes[3],
                'address': attributes[4],
                'products': attributes[5],
                'date': attributes[6],
                'buyer_id': buyer_id  # add the user_id attribute here
            })
    print("done")