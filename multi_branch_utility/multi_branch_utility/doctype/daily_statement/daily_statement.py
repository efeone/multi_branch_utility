# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import *
from multi_branch_utility.multi_branch_utility.utils import *

class DailyStatement(Document):
	def validate(self):
		frappe.throw(_('No Permision To Save!'))


@frappe.whitelist()
def get_daily_statement_values(cost_center, posting_date=today() , payment_type='CASH'):
	statement = []
	sales_details = { 'cash_sales':0, 'credit_sales':0 , 'cash_sales_return':0, 'credit_sales_return':0 , 'cash_sales_total':0, 'credit_sales_total':0, 'total_sales':0 }
	sales_details_count = { 'cash_sales_count':0, 'credit_sales_count':0 , 'cash_sales_return_count':0, 'credit_sales_return_count':0 }
	purchase_details = { 'cash_purchase':0, 'credit_purchase':0 , 'cash_purchase_return':0, 'credit_purchase_return':0, 'cash_purchase_total':0, 'credit_purchase_total':0, 'total_purchase':0 }
	purchase_details_count = { 'cash_purchase_count':0, 'credit_purchase_count':0 , 'cash_purchase_return_count':0, 'credit_purchase_return_count':0 }
	payment_entries = { 'customer_cash':0, 'supplier_cash':0, 'bank_transaction':0, 'journal_entry':0 }
	payment_entries_count = { 'customer_cash_count':0, 'supplier_cash_count':0, 'bank_transaction_count':0, 'journal_entry_count':0 }

	#Sales Details
	sales_details['cash_sales'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice')[0]
	sales_details['credit_sales'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice')[0]
	sales_details['cash_sales_return'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice', 1)[0]
	sales_details['credit_sales_return'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice', 1)[0]
	sales_details['cash_sales_total'] = (sales_details['cash_sales'] + sales_details['cash_sales_return'])
	sales_details['credit_sales_total'] = (sales_details['credit_sales'] + sales_details['credit_sales_return'])
	sales_details['total_sales'] = sales_details['cash_sales_total'] + sales_details['credit_sales_total']

	#Setting Sales Count
	sales_details_count['cash_sales_count'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice')[1]
	sales_details_count['credit_sales_count'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice')[1]
	sales_details_count['cash_sales_return_count'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice', 1)[1]
	sales_details_count['credit_sales_return_count'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice', 1)[1]

	#Purchase Details
	purchase_details['cash_purchase'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice')[0]
	purchase_details['credit_purchase'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice')[0]
	purchase_details['cash_purchase_return'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice', 1)[0]
	purchase_details['credit_purchase_return'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice', 1)[0]
	purchase_details['cash_purchase_total'] = (purchase_details['cash_purchase'] + purchase_details['cash_purchase_return'])
	purchase_details['credit_purchase_total'] = (purchase_details['credit_purchase'] + purchase_details['credit_purchase_return'])
	purchase_details['total_purchase'] = purchase_details['cash_purchase_total'] + purchase_details['credit_purchase_total']

	#Setting Purchase Count
	purchase_details_count['cash_purchase_count'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice')[1]
	purchase_details_count['credit_purchase_count'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice')[1]
	purchase_details_count['cash_purchase_return_count'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice', 1)[1]
	purchase_details_count['credit_purchase_return_count'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice', 1)[1]

	#payment Entires
	cash_mode_of_payment = False
	bank_mode_of_payment = False
	cash_payment_details = get_mode_of_payment('CASH', cost_center)
	bank_payment_details = get_mode_of_payment('BANK', cost_center)
	if cash_payment_details:
		cash_mode_of_payment = cash_payment_details.mode_of_payment
	if bank_payment_details:
		bank_mode_of_payment = bank_payment_details.mode_of_payment
	payment_entries['customer_cash'] = get_payment_entries(posting_date, cost_center, 'Receive', cash_mode_of_payment)[0]
	payment_entries['supplier_cash'] = get_payment_entries(posting_date, cost_center, 'Pay', cash_mode_of_payment)[0]
	payment_entries['bank_transaction'] = get_payment_entries(posting_date, cost_center, 'Receive', bank_mode_of_payment)[0]
	payment_entries['bank_transaction'] = payment_entries['bank_transaction'] - get_payment_entries(posting_date, cost_center, 'Pay', bank_mode_of_payment)[0]
	payment_entries['journal_entry'] = get_journal_entries(posting_date, cost_center)[0]
	payment_entries_count['customer_cash_count'] = get_payment_entries(posting_date, cost_center, 'Receive', cash_mode_of_payment)[1]
	payment_entries_count['supplier_cash_count'] = get_payment_entries(posting_date, cost_center, 'Pay', cash_mode_of_payment)[1]
	payment_entries_count['journal_entry_count'] = get_journal_entries(posting_date, cost_center)[1]
	payment_entries_count['bank_transaction_count'] = get_payment_entries(posting_date, cost_center, 'Pay', bank_mode_of_payment)[1]
	payment_entries_count['bank_transaction_count'] = payment_entries_count['bank_transaction_count'] + get_payment_entries(posting_date, cost_center, 'Receive', bank_mode_of_payment)[1]

	sales_details = format_to_currency(sales_details, 'SAR')
	purchase_details = format_to_currency(purchase_details, 'SAR')
	payment_entries = format_to_currency(payment_entries, 'SAR')

	statement.append(sales_details)
	statement.append(purchase_details)
	statement.append(payment_entries)
	statement.append(sales_details_count)
	statement.append(purchase_details_count)
	statement.append(payment_entries_count)

	html = get_html_content('templates/daily_statement_dashboard.html', statement, getdate(posting_date), cost_center)
	return html

@frappe.whitelist()
def get_total_invoice_amount(posting_date, cost_center, payment_type, doctype, is_return=0):
	query = """
		SELECT
			IFNULL(SUM(rounded_total), 0) as invoice_amount,
			IFNULL(COUNT(*), 0) as invoice_count
		FROM
			`tab{0}` as tab
		WHERE
			tab.payment_type = %(payment_type)s AND
			tab.posting_date = %(posting_date)s AND
			tab.cost_center = %(cost_center)s AND
			tab.is_return = %(is_return)s AND
			tab.docstatus = 1
	"""
	output = frappe.db.sql(query.format(doctype), { 'payment_type': payment_type, 'posting_date': posting_date, 'cost_center': cost_center, 'is_return': is_return }, as_dict=True)
	return (output[0].invoice_amount, output[0].invoice_count)

@frappe.whitelist()
def get_payment_entries(posting_date, cost_center, type, mode_of_payment=None):
	query = """
		SELECT
			IFNULL(SUM(paid_amount), 0) as paid_amount,
			IFNULL(COUNT(*), 0) as count
		FROM
			`tabPayment Entry` as pe
		WHERE
			pe.payment_type = %(payment_type)s AND
			pe.posting_date = %(posting_date)s AND
			pe.cost_center = %(cost_center)s AND
			pe.docstatus = 1
	"""
	if mode_of_payment:
		query = query + "AND pe.mode_of_payment = %(mode_of_payment)s"
	output = frappe.db.sql(query.format(), { 'payment_type': type, 'posting_date': posting_date, 'cost_center': cost_center, 'mode_of_payment': mode_of_payment }, as_dict=True)
	return (output[0].paid_amount, output[0].count)

@frappe.whitelist()
def get_journal_entries(posting_date, cost_center):
	query = """
		SELECT
			IFNULL(SUM(total_debit), 0) as amount,
			IFNULL(COUNT(*), 0) as count
		FROM
			`tabJournal Entry` as je
		WHERE
			je.posting_date = %(posting_date)s AND
			je.cost_center = %(cost_center)s AND
			je.docstatus = 1
	"""
	output = frappe.db.sql(query.format(), { 'posting_date': posting_date, 'cost_center': cost_center }, as_dict=True)
	return (output[0].amount, output[0].count)

@frappe.whitelist()
def format_to_currency(input_dict, currency):
	keys = input_dict.keys()
	for key in keys:
		input_dict[key] = fmt_money(input_dict[key], currency=currency)
	return input_dict

@frappe.whitelist()
def get_html_content(template_path, statement=None, posting_date=None, cost_center=None):
	if statement:
		html = frappe.render_template(template_path, dict(statement=statement, posting_date=posting_date, cost_center=cost_center))
	else:
		html = frappe.render_template(template_path, {})
	return html
