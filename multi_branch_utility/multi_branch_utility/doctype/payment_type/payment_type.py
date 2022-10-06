# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

class PaymentType(Document):
	def validate(self):
		payment_type_list = [ 'CASH', 'CREDIT' , 'BANK' ]
		if self.payment_type and self.payment_type not in payment_type_list:
			frappe.throw(_('Invalid Payment Type!'))

		self.validate_is_default()

		if self.payment_type_accounts:
			company = frappe.get_last_doc('Company')
			for payment_type_account in self.payment_type_accounts:
				payment_amount = get_bank_cash_account(payment_type_account.mode_of_payment, company.name)
				payment_type_account.account = payment_amount['account']

	def validate_is_default(self):
		if self.payment_type_accounts:
			for payment_type_account in self.payment_type_accounts:
				if payment_type_account.is_default and payment_type_account.cost_center:
					for pta in self.payment_type_accounts:
						if pta.cost_center == payment_type_account.cost_center and pta.is_default and pta.mode_of_payment != payment_type_account.mode_of_payment:
							frappe.throw(_('Only one Mode of Payment can set as Default for <b>'+ payment_type_account.cost_center + '</b>.'))
