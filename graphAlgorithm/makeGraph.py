#! /usr/bin/env python3
import pymongo
import openai
import networkx as nx
import matplotlib.pyplot as plt
import random
import copy


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
    G = tree_layout(G)
    return graphToPic(G,username)

def graphToPic(G,username):
    # Draw the graph
    plt.figure(figsize=(20, 20))
    nx.draw_networkx(G, pos=nx.get_node_attributes(G, 'pos'), with_labels=True, node_size=1000, node_color='lightblue', font_size=20)
    plt.axis('off')
    plt.savefig('treeImages/'+username+'.png', bbox_inches='tight', pad_inches=0)
    return 'treeImages/'+username+'.png'


def tree_layout(G):
    # Create a copy of the graph so we don't modify the original
    H = copy.deepcopy(G)

    # Get the edges and nodes of the graph
    edges = list(H.edges())
    nodes = list(H.nodes())

    # Create a dictionary to store the position of each node
    pos = {}

    # Set the position of the root node to (0, 0)
    root_node = nodes[0]
    pos[root_node] = (0, 0)

    # Set the position of the children of the root node
    children = list(H.neighbors(root_node))
    num_children = len(children)
    child_positions = [(i - (num_children - 1) / 2, -1) for i in range(num_children)]
    random.shuffle(child_positions)  # Shuffle the positions to add some randomness
    for i, child in enumerate(children):
        pos[child] = child_positions[i]

    # Recursively set the position of the rest of the nodes
    def set_position(node):
        nonlocal pos
        children = list(H.neighbors(node))
        num_children = len(children)
        if num_children == 0:
            return
        elif num_children == 1:
            child = children[0]
            pos[child] = (pos[node][0], pos[node][1] - 1)
            set_position(child)
        else:
            child_positions = [(i - (num_children - 1) / 2, pos[node][1] - 1) for i in range(num_children)]
            random.shuffle(child_positions)
            for i, child in enumerate(children):
                pos[child] = child_positions[i]
                set_position(child)

    set_position(root_node)

    # Relabel the nodes in the graph with their new positions
    new_labels = {}
    for node, position in pos.items():
        new_label = f"{node} ({position[0]}, {position[1]})"
        new_labels[node] = new_label
    H = nx.relabel_nodes(H, new_labels)

    # Return the new graph with the nodes in a tree layout
    return H

if __name__ == '__main__':
    print(makegraph("Super Home Builder"))