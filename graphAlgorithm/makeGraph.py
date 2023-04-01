import pymongo
import openai
from graphviz import Digraph

def makegraph(userID):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    users_db = client.users
    invoice_db = client.invoices

    # Connect to the ChatGPT API
    openai.api_key = "YOUR_API_KEY"
    model_engine = "text-davinci-002"
    product_keyword = "final product" # keyword to identify the final product being built

    # Retrieve the customer's purchases
    customer = users_db.users.find_one({'_id': userID})
    customer_name = customer['customer_name']
    customer_invoices = invoice_db.invoices.find({'user_id': customer['_id']})

    # Analyze the product descriptions to determine which invoices are relevant
    relevant_invoices = []
    for invoice in customer_invoices:
        product_descriptions = invoice['product_descriptions']
        for product_description in product_descriptions:
            response = openai.Completion.create(
                engine=model_engine,
                prompt=f"Is the following product relevant to the '{product_keyword}'?\n{product_description}",
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.5,
            )
            if response.choices[0].text.strip().lower() == "yes":
                relevant_invoices.append(invoice)

    # Retrieve the suppliers for the relevant invoices
    relevant_supplier_ids = set()
    for invoice in relevant_invoices:
        supplier_id = invoice['supplier_id']
        relevant_supplier_ids.add(supplier_id)
        while 'parent_supplier_id' in invoice:
            parent_supplier_id = invoice['parent_supplier_id']
            supplier = db.suppliers.find_one({'_id': parent_supplier_id})
            if supplier:
                relevant_supplier_ids.add(parent_supplier_id)
            invoice = db.invoices.find_one({'_id': invoice['parent_invoice_id']})

    relevant_suppliers = []
    for supplier_id in relevant_supplier_ids:
        supplier = db.suppliers.find_one({'_id': supplier_id})
        if supplier:
            relevant_suppliers.append(supplier)

    # Generate a flow chart diagram for the customer's relevant suppliers
    dot = Digraph()
    for supplier in relevant_suppliers:
        dot.node(str(supplier['_id']), supplier['name'])
        if 'parent_supplier_id' in supplier:
            parent_supplier = db.suppliers.find_one({'_id': supplier['parent_supplier_id']})
            dot.edge(str(parent_supplier['_id']), str(supplier['_id']))

    dot.format = 'png'
    dot.render(customer_name + '_relevant_suppliers', view=True)

