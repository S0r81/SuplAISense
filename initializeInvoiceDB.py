from pymongo import MongoClient
from static import DocumentExtract2
import os
import time


def reinitialization():
    client = MongoClient(
        "mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    users_db = client.user_login_system
    users_collection = users_db.users
    user_invoices_collection = users_db.invoices

    invoice_dir = "invoices/"
    i = 0
    for file in os.listdir(invoice_dir):
        if file[-4:] == ".pdf":
            print(i)
            print()
            i += 1
            attributes = DocumentExtract2.parseDocument(users_collection, invoice_dir, file)

            # Find user by buyer_name
            user = users_collection.find_one({"customer_name": attributes[3]})

            if user:
                user_id = user["_id"]

                # Save the invoice in the user_invoices collection with the user_id reference
                user_invoices_collection.insert_one({
                    'filename': attributes[0],
                    'pdf_binary': attributes[1],
                    'seller_name': attributes[2],
                    'buyer_name': attributes[3],
                    'address': attributes[4],
                    'products': attributes[5],
                    'date': attributes[6],
                    'user_id': user_id  # add the user_id attribute here
                })

            else:
                print(f"User not found for buyer_name: {attributes[3]}")

    print("done")


reinitialization()

# Example usage
# InitializeInvoiceDB()
