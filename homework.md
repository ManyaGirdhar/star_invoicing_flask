## Recommendation

1. Read Peewee docs
2. Read Flask docs
3. Re-watch the lecture
4. Do the homework
5. Start setting up Library management your project!

## Homework

<!-- * Implement edit and delete of customers -->
* Implement edit and delete of invoices
  * how will you handle automatic delete of invoice items?
* Clean up the JS code
* Fix "calculation" of total amount in backend

### e-Invoicing via Government of Agrabah

Your task is to integrate with an external service for generating `ARN` number for each invoice that is created in your system. Here is the API spec of the portal you have to integrate with:

```txt
BASE URL: https://frappe.school

POST /api/method/generate-pro-einvoice-id

## Example Request Data (JSON):

{
    "customer_name": "John Doe",
    "invoice_id": 3,
    "payable_amount": 3000
}

## Example Response

{
    "arn": "7e4ef9eb"
}
```

Create a new column named `gov_arn` in your invoice model and store the "arn" received from the above API in that.

> Hint: Install and use [this](https://pypi.org/project/requests/).

### Snippets

Person(Model)

# create a new person in database

p = Person(full_name="John Doe") # Person.create(full_name="John Doe")
p.save()

# Read

p = Person.get_by_id(1)

# Update

p.full_name = "Jenny Doe"
p.save()

# Delete

p.delete_instance()

# List

Person.select()
