from pymongo import MongoClient
from static import DocumentExtract2
from flask import make_response

def parese_temp_file(filename):
    client = MongoClient(
        "mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    temp_invoice_db = client.temp_invoices.temp_invoices
    invoice_db = client.user_invoices.user_invoices
    users_db = client.user_login_system.users
    file=temp_invoice_db.find_one({'filename':filename})
    temp_invoice_db.delete_one({'filename':filename})
    file_content= make_response(file["content"])
    if file[filename][-4:] == ".pdf":
        attributes = DocumentExtract2.parseDocument(users_db,file_content)
        # Find user by session
        buyer = users_db.find_one({"name": attributes[3]})
        if buyer:
            buyer_id = buyer["_id"]
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
        else:
            print(f"User not found for buyer_name: {attributes[3]}")
    print("done")