from peewee import Model, CharField, TextField, SqliteDatabase, DateField, FloatField, ForeignKeyField, AutoField, IntegerField

db = SqliteDatabase("invoices.db", pragmas={"foreign_keys": 1})

class Customer(Model):
    full_name = CharField(200)
    address = TextField()

    class Meta:
        database = db


class Invoice(Model):
    invoice_id = AutoField()
    customer = ForeignKeyField(Customer)
    date = DateField()
    total_amount = FloatField()
    tax_percent = FloatField()
    payable_amount = FloatField()
    gov_arn = CharField(null=True)
    class Meta:
        database = db

class InvoiceItem(Model):
    item_name = CharField(200, unique=True)
    qty = IntegerField()
    rate = FloatField()
    amount = FloatField()
    invoice = ForeignKeyField(Invoice, backref="items", lazy_load=False)

    class Meta:
        database = db