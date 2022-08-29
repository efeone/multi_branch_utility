import frappe
import erpnext
from frappe import _
from frappe.model.document import Document
from datetime import date,datetime
from frappe.utils import *
from erpnext.accounts.party import get_party_account

@frappe.whitelist()
def apply_additional_discount(doc, method):
	if doc.additional_discount_account and doc.additional_discount_amount:
		discount_amount = doc.additional_discount_amount
		for ref in doc.references:
			if ref.outstanding_amount > 0 and discount_amount > 0:
				allocated_amount = 0
				if ref.outstanding_amount == discount_amount:
					allocated_amount = ref.outstanding_amount
				elif ref.outstanding_amount < discount_amount:
					allocated_amount = discount_amount - ref.outstanding_amount
				elif ref.outstanding_amount > discount_amount:
					allocated_amount = ref.outstanding_amount - discount_amount
				journal_entry = frappe.new_doc('Journal Entry')
				journal_entry.voucher_type = 'Journal Entry'
				journal_entry.company = doc.company
				journal_entry.posting_date =  doc.posting_date
				party_type = 'Customer'
				party_account = get_party_account(party_type, doc.party, doc.company)
				accounts = []
				accounts.append({
						'account': party_account,
						'credit_in_account_currency': allocated_amount,
						'party_type': 'Customer',
						'party': doc.party,
						'reference_type':ref.reference_doctype,
						'reference_name': ref.reference_name
					}
				)
				accounts.append({
					'account': doc.additional_discount_account,
					'debit_in_account_currency': allocated_amount,
					'party_type': 'Customer',
					'party': doc.party
				})
				journal_entry.set('accounts', accounts)
				journal_entry.save(ignore_permissions = True)
				journal_entry.submit()
				discount_amount = discount_amount - allocated_amount

@frappe.whitelist()
def get_last_si_rate(customer, item):
	customer_si = frappe.db.get_all('Sales Invoice', filters={'customer': customer, 'docstatus': 1})
	for si in customer_si:
		sales_invoice = frappe.get_doc('Sales Invoice', si.name)
		for si_item in sales_invoice.items :
			if si_item.item_code == item:
				return si_item.rate
	return 0

@frappe.whitelist()
def get_last_po_rate(item):
	item_po = frappe.db.get_all('Purchase Order', filters={'docstatus': 1})
	for po in item_po:
		purchase_order = frappe.get_doc('Purchase Order', po.name)
		for po_item in purchase_order.items:
			if po_item.item_code == item:
				return po_item.rate
	return 0

@frappe.whitelist()
def get_avg_cost(item):
	stock_ledger_entry = frappe.get_last_doc('Stock Ledger Entry', filters={'item_code':item})
	return stock_ledger_entry.valuation_rate