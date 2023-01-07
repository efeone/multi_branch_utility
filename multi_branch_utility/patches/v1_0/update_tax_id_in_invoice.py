from __future__ import unicode_literals
import frappe

def execute():
    frappe.enqueue(update_tax_id, queue='long')


def update_tax_id():
    sales_invoice_list = frappe.db.get_list('Sales Invoice')
    for sales_invoice in sales_invoice_list:
        sales_invoice_customer = frappe.db.get_value('Sales Invoice',sales_invoice.name,'customer')
        cutomer_tax_id = frappe.db.get_value('Customer',sales_invoice_customer,'tax_id')
        if cutomer_tax_id:
            frappe.db.set_value('Sales Invoice', sales_invoice.name, 'tax_id', cutomer_tax_id)
    frappe.db.commit()
