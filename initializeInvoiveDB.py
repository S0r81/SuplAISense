#!/usr/bin/env python3
from pymongo import MongoClient
from static import DocumentExtract2
import os
import time

#add progress bar
#for each file in the invoice directory extract the information using static/DocumentExtract2.py and save it to the mongodb database
client = MongoClient("mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
db = client.invoices
invoice_dir = "invoices/"
i=0
for file in os.listdir(invoice_dir):
    if file[-4:] == ".pdf":
        print(i)
        print()
        i+=1
        attributes=DocumentExtract2.parseDocument(invoice_dir,file)
        db.invoices.insert_one({'filename': attributes[0], 'pdf_binary': attributes[1], 'seller_name': attributes[2], 'buyer_name': attributes[3], 'address': attributes[4], 'products': attributes[5], 'date': attributes[6]})

print("done")