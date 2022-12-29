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
	if frappe.db.get_single_value('Multi Branch Settings', 'allow_payment_entry'):
		if doc.payment_type == 'CASH':
			from multi_branch_utility.multi_branch_utility.utils import get_mode_of_payment
			payment_type_details = get_mode_of_payment(doc.payment_type, doc.cost_center)
			if not payment_type_details:
				frappe.throw('Please set Mode of Payment in Payment Type CASH')
			if payment_type_details:
				if not doc.is_return and doc.payment_type and doc.payment_type == 'CASH' and payment_type_details.mode_of_payment and payment_type_details.account:
					company = frappe.get_last_doc('Company')
					if doc.doctype == "Sales Invoice":
						reference_doctype = doc.doctype
						party_type = "Customer"
						party = doc.customer
						paid_to = payment_type_details.account
						paid_from =  get_party_account(party_type, party, company.name)
						payment_type = "Receive"
					if doc.doctype == "Purchase Invoice":
						reference_doctype = doc.doctype
						party_type = "Supplier"
						party = doc.supplier
						paid_from = payment_type_details.account
						paid_to =  get_party_account(party_type, party, company.name)
						payment_type = "Pay"
					pay = frappe.new_doc('Payment Entry')
					pay.payment_type = payment_type
					pay.mode_of_payment = payment_type_details.mode_of_payment
					pay.posting_date = doc.posting_date
					pay.party_type = party_type
					pay.party = party
					pay.paid_from = paid_from
					pay.source_exchange_rate = 1
					pay.paid_amount = doc.outstanding_amount
					pay.received_amount = doc.outstanding_amount
					pay.paid_to = paid_to
					pay.cost_center = doc.cost_center
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

@frappe.whitelist()
def stock_entry_before_validate(doc, method):
	for item in doc.items:
		if item.item_code:
			item_doc = frappe.get_doc('Item', item.item_code)
			if item_doc.cost_center:
				item.cost_center = item_doc.cost_center
			elif item.s_warehouse:
				warehouse = frappe.get_doc('Warehouse', item.s_warehouse)
				if warehouse.cost_center:
					item.cost_center = warehouse.cost_center
			elif item.t_warehouse:
				warehouse = frappe.get_doc('Warehouse', item.t_warehouse)
				if warehouse.cost_center:
					item.cost_center = warehouse.cost_center
