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
	purchase_details = { 'cash_purchase':0, 'credit_purchase':0 , 'cash_purchase_return':0, 'credit_purchase_return':0, 'cash_purchase_total':0, 'credit_purchase_total':0, 'total_purchase':0 }
	payment_entries = { 'customer_cash':0, 'customer_cheque':0, 'supplier_cash':0, 'supplier_cheque':0, 'bank_transaction':0, 'journal_entry':0 }

	#Sales Details
	sales_details['cash_sales'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice')
	sales_details['credit_sales'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice')
	sales_details['cash_sales_return'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Sales Invoice', 1)
	sales_details['credit_sales_return'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Sales Invoice', 1)
	sales_details['cash_sales_total'] = (sales_details['cash_sales'] + sales_details['cash_sales_return'])
	sales_details['credit_sales_total'] = (sales_details['credit_sales'] + sales_details['credit_sales_return'])
	sales_details['total_sales'] = sales_details['cash_sales_total'] + sales_details['credit_sales_total']

	#Purchase Details
	purchase_details['cash_purchase'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice')
	purchase_details['credit_purchase'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice')
	purchase_details['cash_purchase_return'] = get_total_invoice_amount(posting_date, cost_center, 'CASH', 'Purchase Invoice', 1)
	purchase_details['credit_purchase_return'] = get_total_invoice_amount(posting_date, cost_center, 'CREDIT', 'Purchase Invoice', 1)
	purchase_details['cash_purchase_total'] = (purchase_details['cash_purchase'] + purchase_details['cash_purchase_return'])
	purchase_details['credit_purchase_total'] = (purchase_details['credit_purchase'] + purchase_details['credit_purchase_return'])
	purchase_details['total_purchase'] = purchase_details['cash_purchase_total'] + purchase_details['credit_purchase_total']

	#payment Entires
	mode_of_payment = ""
	payment_details = get_mode_of_payment('CASH', cost_center)
	if payment_details:
		mode_of_payment = payment_details.mode_of_payment
	payment_entries['customer_cash'] = get_payment_entries(posting_date, cost_center, 'Receive', mode_of_payment)
	payment_entries['supplier_cash'] = get_payment_entries(posting_date, cost_center, 'Pay', mode_of_payment)

	sales_details = format_to_currency(sales_details, 'SAR')
	purchase_details = format_to_currency(purchase_details, 'SAR')
	payment_entries = format_to_currency(payment_entries, 'SAR')

	statement.append(sales_details)
	statement.append(purchase_details)
	statement.append(payment_entries)

	html = get_html_content('templates/daily_statement_dashboard.html', statement)
	return html

@frappe.whitelist()
def get_total_invoice_amount(posting_date, cost_center, payment_type, doctype, is_return=0):
	query = """
		SELECT
			IFNULL(SUM(rounded_total), 0) as invoice_amount
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
	return output[0].invoice_amount

@frappe.whitelist()
def get_payment_entries(posting_date, cost_center, type, mode_of_payment=None):
	query = """
		SELECT
			IFNULL(SUM(paid_amount), 0) as paid_amount
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
	return output[0].paid_amount

@frappe.whitelist()
def format_to_currency(input_dict, currency):
	keys = input_dict.keys()
	for key in keys:
		input_dict[key] = fmt_money(input_dict[key], currency=currency)
	return input_dict

@frappe.whitelist()
def get_html_content(template_path, statement=None):
	if statement:
		html = frappe.render_template(template_path, dict(statement=statement))
	else:
		html = frappe.render_template(template_path, {})
	return html
