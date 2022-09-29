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
def get_last_pr_rate(item):
	item_pr = frappe.db.get_all('Purchase Receipt', filters={'docstatus': 1})
	for pr in item_pr:
		purchase_receipt = frappe.get_doc('Purchase Receipt', pr.name)
		for pr_item in purchase_receipt.items:
			if pr_item.item_code == item:
				return pr_item.rate
	return 0

@frappe.whitelist()
def get_avg_cost(item):
	stock_ledger_entry = frappe.get_last_doc('Stock Ledger Entry', filters={'item_code':item})
	return stock_ledger_entry.valuation_rate

@frappe.whitelist()
def set_import_missing_values(doc, method):
	if doc.items:
		for item in doc.items:
			if not item.income_account:
				item.income_account = frappe.get_cached_value("Company", doc.company, "default_income_account")
				item.description = item.item_name
	if not doc.cost_center:
		doc.cost_center = frappe.get_cached_value("Customer", doc.customer, "cost_center")

@frappe.whitelist()
def make_payment(doc, method):
	if frappe.db.get_single_value('Multi Branch Settings','allow_payment_entry'):
		if not doc.is_return and doc.payment_type and doc.payment_type=='CASH':
			mode_of_payment = frappe.get_doc("Mode of Payment", 'Cash')
			mode_of_payment_account = mode_of_payment.accounts[0].default_account
			company = frappe.get_last_doc('Company')
			if doc.doctype == "Sales Invoice":
				reference_doctype = doc.doctype
				party_type = "Customer"
				party = doc.customer
				paid_to = mode_of_payment_account
				paid_from = company.default_receivable_account
				payment_type = "Receive"			
			if doc.doctype == "Purchase Invoice":
				reference_doctype = doc.doctype
				party_type = "Supplier"
				party = doc.supplier	
				paid_from = mode_of_payment_account
				paid_to = company.default_payable_account	
				payment_type = "Pay"	
			pay = frappe.new_doc('Payment Entry')
			pay.payment_type = payment_type
			pay.mode_of_payment = "Cash"
			pay.party_type = party_type
			pay.party = party
			pay.paid_from = paid_from
			pay.source_exchange_rate = 1
			pay.paid_amount = doc.outstanding_amount
			pay.received_amount = doc.outstanding_amount
			pay.paid_to = paid_to
			pay.append("references",{
				"reference_doctype" : reference_doctype,
				"reference_name": doc.name,
				"total_amount": doc.grand_total,
				"outstanding_amount": doc.outstanding_amount,
				"allocated_amount": doc.outstanding_amount
			})
			pay.submit()
			frappe.msgprint(msg='Payment Enrty against '+ doc.name + ' is completed', title='Message', alert="True")
			doc.reload()
