# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

class SalesInvoiceCounter(Document):
	pass

@frappe.whitelist()
def make_payment(self):
	doc=frappe.get_doc("Sales Invoice",self)
	if frappe.db.get_single_value('Multi Branch Settings','allow_payment_entry'):
		if not doc.is_return and doc.payment_type and doc.payment_type=='CASH':
			mode_of_payment = frappe.get_doc("Mode of Payment", 'Cash')
			mode_of_payment_account = mode_of_payment.accounts[0].default_account
			company = frappe.get_last_doc('Company')
			pay = frappe.new_doc('Payment Entry')
			pay.payment_type = 'Receive'
			pay.mode_of_payment = "Cash"
			pay.party_type = 'Customer'
			pay.party = doc.customer
			pay.paid_from = company.default_receivable_account
			pay.source_exchange_rate = 1
			pay.paid_amount = doc.outstanding_amount
			pay.received_amount = doc.outstanding_amount
			pay.paid_to = mode_of_payment_account
			pay.append("references",{
			"reference_doctype" : doc.doctype,
			"reference_name": doc.name,
			"total_amount": doc.grand_total,
			"outstanding_amount": doc.outstanding_amount,
			"allocated_amount": doc.outstanding_amount
			})
			pay.submit()
			return pay
