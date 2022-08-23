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
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Journal Entry'
		journal_entry.company = doc.company
		journal_entry.posting_date =  doc.posting_date
		party_type = 'Customer'
		party_account = get_party_account(party_type, doc.party, doc.company)
		accounts = []
		accounts.append({
				'account': party_account,
				'credit_in_account_currency': doc.additional_discount_amount,
				'party_type': 'Customer',
				'party': doc.party
			}
		)
		accounts.append({
			'account': doc.additional_discount_account,
			'debit_in_account_currency': doc.additional_discount_amount,
			'party_type': 'Customer',
			'party': doc.party
		})
		journal_entry.set('accounts', accounts)
		journal_entry.save(ignore_permissions = True)
		journal_entry.submit()
