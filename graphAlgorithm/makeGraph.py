#! /usr/bin/env python3
import pymongo
import openai
import networkx as nx
import matplotlib.pyplot as plt
from graphviz import Digraph


def makegraph(username):
    # Connect to the MongoDB database
    client = pymongo.MongoClient(
        "mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    users_db = client.users
    invoice_db = client.invoices

    # Connect to the ChatGPT API
    openai.api_key = "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"
    model_engine = "text-davinci-002"
    product_keyword = "any product"  # keyword to identify the final product being built

    # Retrieve the customer's purchases
    customer = users_db.users.find_one({'customer_name': username})
    customer_invoices = invoice_db.invoices.find({'buyer_name': username})

    # Analyze the product descriptions to determine which invoices are relevant
    connections = [[username, i['seller_name'], '\n'.join([a for a,b in i['products']])] for i in customer_invoices]
    relevant_invoices = [[i, "any product"] for i in customer_invoices]
    while relevant_invoices:
        invoice, product_target = relevant_invoices.pop(0)
        print(invoice['filename'])
        for product_keyword, quantity in invoice['products']:
            response = openai.Completion.create(
                engine=model_engine,
                prompt=f"Respond yes or no. Is {product_keyword} used in the production of {product_target} respond yes or no do not include an explanation'?\n",
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.5,
            )
            if response.choices[0].text.strip().lower() == "yes":
                print({'customer_name': invoice['seller_name']})
                for invoice in users_db.users.find_one({'customer_name': invoice['seller_name']}):
                    relevant_invoices.append([invoice, product_keyword])
                    connections.append([invoice['seller_name'], invoice['buyer_name'], product_keyword[0]])

    # Create an empty graph
    G = nx.Graph()

    # Add nodes to the graph for each supplier and buyer
    for connection in connections:
        supplier, buyer, _ = connection
        G.add_node(supplier)
        G.add_node(buyer)

    # Add edges to the graph for each connection with the product information
    for connection in connections:
        supplier, buyer, product = connection
        G.add_edge(supplier, buyer, product=str(product))

    # # Draw the graph with nodes labeled by their names and edges labeled by the product
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'product')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_weight='bold')
    plt.show()


if __name__ == '__main__':
    makegraph("Super Home Builder")