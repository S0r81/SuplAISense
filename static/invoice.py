from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from faker import Faker
import os
import random


def generate_dates(fake):
    date_formats = [
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%A, %B %d, %Y",
        "%A, %d %B %Y",
        "%m-%d-%y",
        "%d-%m-%y"
    ]

    return [fake.date_time_between(start_date='-5y', end_date='now').strftime(date_format) for date_format in
            date_formats]


def generate_invoice_items(num_items=5):
    lumber_items = [
        "Softwood Lumber",
        "Hardwood Lumber",
        "Plywood",
        "OSB",
        "Particle Board",
        "MDF",
        "Dimensional Lumber",
        "Engineered Wood",
        "Wooden Beams",
        "Wooden Poles"
    ]

    items = []
    for _ in range(num_items):
        description = random.choice(lumber_items)
        quantity = random.randint(1, 10)
        price = round(random.uniform(50, 500), 2)
        subtotal = round(quantity * price, 2)
        items.append({"description": description, "quantity": quantity, "price": price, "subtotal": subtotal})

    return items


def generate_invoice(fake, date, i, j, template):
    items = generate_invoice_items(num_items=random.randint(5, 10))
    total = round(sum(item['subtotal'] for item in items), 2)
    tax_rate = 0.07
    tax_amount = round(total * tax_rate, 2)
    grand_total = round(total + tax_amount, 2)

    invoice_number = fake.random_number(digits=6)

    # Company and customer details
    company_name = "Lumber Mill Company"
    company_address = "123 Lumber Mill St"
    company_city = "Portland"
    company_state = "OR"
    company_zipcode = "97201"
    customer_name = "Lumber Jack Company"
    customer_address = "456 Lumber Jack St"
    customer_city = "Salem"
    customer_state = "OR"
    customer_zipcode = "97301"

    doc = SimpleDocTemplate(os.path.join("invoices", f"invoice_{i}_{j}.pdf"), pagesize=letter)

    # Set up styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="InvoiceTitle", fontSize=20, leading=24))
    styles.add(ParagraphStyle(name="InvoiceSubtitle", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="InvoiceFieldLabel", fontSize=10, leading=12))
    styles.add(ParagraphStyle(name="InvoiceFieldText", fontSize=10, leading=12))

    # Invoice title
    invoice_title = Paragraph("Invoice", styles["InvoiceTitle"])

    # Invoice metadata
    invoice_info = [
        ["Invoice Number:", invoice_number, "Date:", date],
        ["Company:", company_name, "Customer:", customer_name],
        ["Company Address:", company_address, "Customer Address:", customer_address],
        ["City, State, ZIP:", f"{company_city}, {company_state} {company_zipcode}", "City, State, ZIP:",
         f"{customer_city}, {customer_state} {customer_zipcode}"]
    ]
    invoice_info_table = Table(invoice_info, colWidths=[100, 200, 100, 200])
    invoice_info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (0, -1), colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 12)
    ]))

    # Line items
    item_rows = [["Description", "Qty", "Unit Price", "Amount"]]
    for item in items:
        item_rows.append([item['description'], item['quantity'], f"${item['price']}", f"${item['subtotal']}"])
    item_rows.append(["", "", "Subtotal:", f"${total}"])
    item_rows.append(["", "", f"Tax ({tax_rate * 100}%):", f"${tax_amount}"])
    item_rows.append(["", "", "Total:", f"${grand_total}"])
    line_items = Table(item_rows, colWidths=[300, 50, 100, 100])
    line_items.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("LEADING", (0, 0), (-1, 0), 14),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("LEADING", (0, 1), (-1, -1), 12)
    ]))

    # Assemble the document
    story = [invoice_title, Spacer(1, 12), invoice_info_table, Spacer(1, 24), line_items]
    doc.build(story)


def main():
    fake = Faker()
    output_folder = "invoices"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(5):
        dates = generate_dates(fake)
        for j, date in enumerate(dates):
            template = (i + j) % 2 + 1
            generate_invoice(fake, date, i, j, template)


if __name__ == "__main__":
    main()

