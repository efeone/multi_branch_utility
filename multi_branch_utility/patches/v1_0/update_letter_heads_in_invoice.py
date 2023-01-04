from __future__ import unicode_literals
import frappe

def execute():
    frappe.enqueue(update_letter_head, queue='long')

def update_letter_head():
    if frappe.db.exists('Sales Invoice', { 'cost_center': 'Gateway EVD - AAC', 'letter_head': 'Al Amthal Gateway Wholesale' }):
        sales_invoice_list = frappe.db.get_list('Sales Invoice', filters={'cost_center': 'Gateway EVD - AAC', 'letter_head': 'Al Amthal Gateway Wholesale'})
        for sales_invoice in sales_invoice_list:
            frappe.db.set_value('Sales Invoice', sales_invoice.name, 'letter_head', 'Gateway EVD')
        frappe.db.commit()
