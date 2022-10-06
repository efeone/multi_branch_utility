import frappe
from frappe.utils import *
from frappe import _

@frappe.whitelist()
def get_mode_of_payment(payment_type, cost_center):
    payment_type_details = ''
    payment_type_doc = frappe.get_doc('Payment Type', payment_type )
    if payment_type_doc.payment_type_accounts:
        for payment_type_account in payment_type_doc.payment_type_accounts:
            if not payment_type_details or payment_type_account.is_default == 1:
                if payment_type_account.cost_center == cost_center:
                    payment_type_details = payment_type_account
    return payment_type_details

@frappe.whitelist()
def get_last_si_rate(customer, item):
	if frappe.db.exists('Sales Invoice',{'customer':customer, 'docstatus': 1}):
		customer_si = frappe.db.get_all('Sales Invoice', filters={'customer': customer, 'docstatus': 1})
		for si in customer_si:
			sales_invoice = frappe.get_doc('Sales Invoice', si.name)
			for si_item in sales_invoice.items :
				if si_item.item_code == item:
					return si_item.rate
		return 0

@frappe.whitelist()
def get_last_pr_rate(item):
	if frappe.db.exists('Purchase Receipt',{'docstatus': 1}):
		item_pr = frappe.db.get_all('Purchase Receipt', filters={'docstatus': 1})
		for pr in item_pr:
			purchase_receipt = frappe.get_doc('Purchase Receipt', pr.name)
			for pr_item in purchase_receipt.items:
				if pr_item.item_code == item:
					return pr_item.rate
		return 0

@frappe.whitelist()
def get_avg_cost(item):
	if frappe.db.exists('Stock Ledger Entry',{'item_code':item}):
		stock_ledger_entry = frappe.get_last_doc('Stock Ledger Entry', filters={'item_code':item})
		return stock_ledger_entry.valuation_rate
