import os
import pymongo
import requests
from pymongo import MongoClient
from glob import glob
from six import BytesIO


class NaryTreeNode:
    def __init__(self, invoice, children=None):
        self.invoice = invoice
        self.children = children if children is not None else []

    def add_child(self, child):
        self.children.append(child)


# Set up connection to MongoDB
client = pymongo.MongoClient("mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
db = client["social_network"]
users = db["users"]


def generate_suggestions(node):
    # Load the invoice file
    with open(node.invoice, "rb") as f:
        invoice_bytes = f.read()

    # Convert the invoice file to plain text using OCR
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-ocr/analyze",
        headers={"Content-Type": "application/octet-stream"},
        data=BytesIO(invoice_bytes),
    )
    if response.status_code != 200:
        raise ValueError("OCR analysis failed")
    response_json = response.json()
    text = response_json["text"]

    # Query MongoDB for suggested connections
    suggestions = []
    for user in users.find():
        if user["interests"] and any(word in text.lower() for word in user["interests"]):
            suggestions.append(user["name"])

    return suggestions


def find_neighbors(node, depth):
    neighbors = []

    if depth == 0:
        return neighbors

    # Generate suggestions for the current node's invoice
    suggestions = generate_suggestions(node)

    for suggestion in suggestions:
        suggestion_node = NaryTreeNode(suggestion)
        node.add_child(suggestion_node)
        neighbors.append(suggestion)

    # Recursively search for neighbors at a lower depth
    for child in node.children:
        neighbors.extend(find_neighbors(child, depth - 1))

    return neighbors


def main():
    root = NaryTreeNode("root")

    # Iterate over existing invoices
    invoice_files = glob(os.path.join("invoices", "*.pdf"))
    all_suggestions = []
    for invoice_file in invoice_files:
        # Add invoice to the tree
        invoice_node = NaryTreeNode(invoice_file)
        root.add_child(invoice_node)

        # Generate suggestions for the invoice
        with open(invoice_file, "rb") as f:
            invoice_bytes = f.read()

        response = requests.post(
            "https://api.openai.com/v1/engines/davinci-ocr/analyze",
            headers={"Content-Type": "application/octet-stream"},
            data=BytesIO(invoice_bytes),
        )
        if response.status_code != 200:
            raise ValueError("OCR analysis failed")
        response_json = response.json()
        text = response_json["text"]

        suggestions = []
        for user in users.find():
            if user["interests"] and any(word in text.lower() for word in user["interests"]):
                suggestions.append(user["name"])

        all_suggestions.append(suggestions)

        # Add suggested connections to the tree
        for suggestion in suggestions:
            suggestion_node = NaryTreeNode(suggestion)
            invoice_node.add_child(suggestion_node)

    # Find neighbors at a given depth
    target_depth = 2
    neighbors = find_neighbors(root, target_depth)

    # Collect all suggestions into a list of lists
    all_suggestions_formatted = []
    for i, suggestions in enumerate(all_suggestions):
        suggestion_dict = {"invoice": invoice_files[i], "suggestions": suggestions}
        all_suggestions_formatted.append(suggestion_dict)

    return all_suggestions_formatted


if __name__ == "__main__":
    main()
