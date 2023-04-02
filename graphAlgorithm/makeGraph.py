#! /usr/bin/env python3
import pymongo
import openai
import networkx as nx
import matplotlib.pyplot as plt


def makegraph(username):
    # Connect to the MongoDB database
    client = pymongo.MongoClient(
        "mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
    invoice_db = client.invoices

    # Connect to the ChatGPT API
    openai.api_key = "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"
    model_engine = "text-davinci-002"
    product_keyword = "any product"  # keyword to identify the final product being built

    # Retrieve the customer's purchases
    customer_invoices = list(invoice_db.invoices.find({'buyer_name': username}))

    # Analyze the product descriptions to determine which invoices are relevant
    connections = [[username, i['seller_name'], '\n'.join([a for a,b in i['products']])] for i in customer_invoices]
    relevant_invoices = [[i, "any product"] for i in customer_invoices]
    while relevant_invoices:
        invoice, product_target = relevant_invoices.pop(0)
        print(invoice['filename'])
        for product_keyword, quantity in invoice['products']:
            response = openai.Completion.create(
                engine=model_engine,
                prompt=f"Respond yes or no. Is {product_keyword} similar to the materials used in the production of {product_target} respond yes or no do not include an explanation if you are not very sure say yes'?\n",
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.5,
            )
            if response.choices[0].text.strip().lower() == "yes":
                connections.append([invoice['seller_name'], invoice['buyer_name'], product_keyword])
                query_results=invoice_db.invoices.find({'buyer_name': invoice['seller_name']})
                if query_results:
                    for invoice in query_results:
                        relevant_invoices.append([invoice, product_keyword])

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
    return convert_to_tree(G,username)


def convert_to_tree(G,username):
    # Use the Reingold-Tilford algorithm to create a tree-like structure
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    
    # Draw the tree-like structure
    nx.draw(G, pos, with_labels=True)
    
    edge_labels = nx.get_edge_attributes(G, 'product')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_weight='bold')

    # Show the plot
    plt.savefig(f"treeImages/{username}.png")
    return f"treeImages/{username}.png"


if __name__ == '__main__':
    print(makegraph("Super Home Builder"))