# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

class PaymentType(Document):
	def validate(self):
		payment_type_list = [ 'CASH', 'CREDIT' , 'BANK' ]
		company = frappe.get_last_doc('Company')
		if self.payment_type and self.payment_type not in payment_type_list:
			frappe.throw(_('Invalid Payment Type!'))

		if self.payment_type_accounts:
			for payment_type_account in self.payment_type_accounts:
				payment_amount = get_bank_cash_account(payment_type_account.mode_of_payment, company.name)
				payment_type_account.account = payment_amount['account']
