# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartyRepayment(Document):
	def on_submit(self):
		if self.paid_to and self.paid_from:
			journal_entry = frappe.new_doc("Journal Entry")
			journal_entry.posting_date = self.posting_date
			journal_entry.company = self.company
			amount = self.paid_amount if self.payment_type == 'Pay' else self.received_amount
			if self.payment_type == 'Pay':
				debit_entry = {
				"account": self.paid_to,
				"credit_in_account_currency": amount,
				"cost_center": self.cost_center
				}
				credit_entry = {
					"account": self.paid_from,
					"debit_in_account_currency": amount,
					"party_type": self.party_type,
					"party": self.party,
					"cost_center": self.cost_center
				}
			else:
				debit_entry = {
					"account": self.paid_to,
					"credit_in_account_currency": amount,
					"party_type": self.party_type,
					"party": self.party,
					"cost_center": self.cost_center
				}
				credit_entry = {
					"account": self.paid_from,
					"debit_in_account_currency": amount,
					"cost_center": self.cost_center
				}
			journal_entry.append("accounts", debit_entry)
			journal_entry.append("accounts", credit_entry)
			journal_entry.save()
			journal_entry.submit()
			self.db_set('reference_jv', journal_entry.name)

	def on_cancel(self):
		if self.reference_jv:
			frappe.get_doc("Journal Entry", self.reference_jv).cancel()

