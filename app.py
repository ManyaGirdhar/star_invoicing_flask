import json

from flask import Flask, render_template, request, redirect, make_response, url_for

import requests

from peewee import SqliteDatabase, IntegrityError

from models import Customer, Invoice, InvoiceItem

from weasyprint import HTML

app = Flask(__name__)

db = SqliteDatabase("invoices.db")
db.create_tables([Customer, Invoice, InvoiceItem])

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/new-customer")
def create_customer_form():
    return render_template("create-customer.html")


@app.route("/customers", methods=["POST", "GET"])
def customers():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        address = request.form.get("address")

        customer = Customer(full_name=full_name, address=address)
        customer.save()
        return redirect("/customers")

    else:
        customers = Customer.select()
        return render_template("list-customer.html", customers=customers)





@app.route("/edit_customer/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    customer = Customer.get_or_none(Customer.id == customer_id)
    
    if not customer:
        return "Customer not found", 404  # Handle case where customer does not exist

    if request.method == "POST":
        try:
            customer.full_name = request.form["full_name"]
            customer.address = request.form["address"]
            customer.save()  # Save the updated data to the database
            return redirect(url_for("customers"))  # Redirect back to the list
        except IntegrityError:
            return "Error updating customer", 500  # Handle database errors

    return render_template("edit-customer.html", customer=customer)  # Render the edit form


@app.route("/delete_customer/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    try:
        customer = Customer.get(Customer.id == customer_id)
        customer.delete_instance(recursive=True)  # Deletes customer and related invoices & items
    except IntegrityError:
        pass  # Handle errors if necessary
    return redirect("/customers")



@app.route("/edit_invoice/<int:invoice_id>", methods=["GET", "POST"])
def edit_invoice(invoice_id):
    invoice = Invoice.get_or_none(Invoice.invoice_id == invoice_id)

    if not invoice:
        return "Invoice not found", 404  # Handle missing invoice

    if request.method == "POST":
        # Update invoice details from form data
        invoice.total_amount = float(request.form["total_amount"])
        invoice.tax_percent = float(request.form["tax_percent"])
        invoice.payable_amount = invoice.total_amount + (invoice.total_amount * invoice.tax_percent / 100)
        invoice.save()

        return redirect(url_for("invoices"))  # Redirect back to the invoices list

    return render_template("edit-invoice.html", invoice=invoice)





# Delete Invoice
@app.route("/delete_invoice/<int:invoice_id>", methods=["POST"])
def delete_invoice(invoice_id):
    try:
        invoice = Invoice.get(Invoice.invoice_id == invoice_id)
        invoice.delete_instance(recursive=True)  # Deletes invoice and related items
    except IntegrityError:
        pass  # Handle errors if necessary
    return redirect("/invoices")  # Redirect to the invoices page after deletion





@app.route("/new-invoice")
def create_invoice_form():
    customers = Customer.select()
    return render_template("create-invoice.html", customers=customers)


@app.route("/invoices", methods=["GET", "POST"])
def invoices():
    if request.method == "POST":
        data = request.form
        tax_percent = float(data.get("tax_percent"))
        items_json = data.get("invoice_items")
        items = json.loads(items_json)

        # Calculate total_amount dynamically from invoice items
        total_amount = sum(int(item.get("qty")) * float(item.get("price")) for item in items)

        invoice = Invoice(
            customer=data.get("customer"),
            date=data.get("date"),
            total_amount=total_amount,
            tax_percent=tax_percent,
            payable_amount=total_amount + (total_amount * tax_percent) / 100,
        )

        invoice.save()

        for item in items:
            InvoiceItem(
                invoice=invoice,
                item_name=item.get("item_name"),
                qty=item.get("qty"),
                rate=item.get("price"),
                amount=int(item.get("qty")) * float(item.get("price"))
            ).save()

        # Call API to generate ARN
        arn = generate_arn(invoice)
        print(arn)

        # Update invoice with ARN
        invoice.gov_arn = arn
        invoice.save()


        return redirect("/invoices")
    else:
        return render_template("list-invoice.html", invoices=Invoice.select())


# External API Configuration
BASE_URL = "https://frappe.school"
ARN_API_ENDPOINT = "/api/method/generate-pro-einvoice-id"
# Function to Call External API and Retrieve ARN
def generate_arn(invoice):
    """Sends invoice details to the API to get an ARN number."""
    try:
        response = requests.post(
            f"{BASE_URL}{ARN_API_ENDPOINT}",
            json={
                "customer_name": invoice.customer.full_name,
                "invoice_id": invoice.invoice_id,
                "payable_amount": invoice.payable_amount
            }
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("arn", "None")  # Return ARN or None if not found
        else:
            print(f"Failed to fetch ARN. Status Code: {response.status_code}")
            return None  # Handle failures gracefully
    except Exception as e:
        print(f"Error fetching ARN: {str(e)}")
        return None  # Handle exceptions gracefully




@app.route("/download/<int:invoice_id>")
def download_pdf(invoice_id):
    # get the invoice
    invoice = Invoice.get_by_id(invoice_id)

    # generate the PDF
    html = HTML(string=render_template("print/invoice.html", invoice=invoice))
    response = make_response(html.write_pdf())

    response.headers["Content-Type"] = "application/pdf"

    # send it back to the user
    return response

