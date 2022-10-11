import frappe
from frappe.utils import *
from frappe import _

@frappe.whitelist()
def get_mode_of_payment(payment_type, cost_center):
    payment_type_details = ''
    payment_type_doc = frappe.get_doc('Payment Type', payment_type )
    if payment_type_doc.payment_type_accounts:
        for payment_type_account in payment_type_doc.payment_type_accounts:
            if not payment_type_details or payment_type_account.is_default == 1:
                if payment_type_account.cost_center == cost_center:
                    payment_type_details = payment_type_account
    return payment_type_details

@frappe.whitelist()
def get_last_si_rate(customer, item):
    if frappe.db.exists('Sales Invoice',{'customer':customer, 'docstatus': 1}):
        customer_si = frappe.db.get_all('Sales Invoice', filters={'customer': customer, 'docstatus': 1})
        for si in customer_si:
            sales_invoice = frappe.get_doc('Sales Invoice', si.name)
            for si_item in sales_invoice.items :
                if si_item.item_code == item:
                    return si_item.rate
    return 0

@frappe.whitelist()
def get_last_pr_rate(item):
    if frappe.db.exists('Purchase Receipt',{'docstatus': 1}):
        item_pr = frappe.db.get_all('Purchase Receipt', filters={'docstatus': 1})
        for pr in item_pr:
            purchase_receipt = frappe.get_doc('Purchase Receipt', pr.name)
            for pr_item in purchase_receipt.items:
                if pr_item.item_code == item:
                    return pr_item.rate
    return 0

@frappe.whitelist()
def get_avg_cost(item):
    avg_cost = 0
    if frappe.db.exists('Stock Ledger Entry',{'item_code':item}):
        stock_ledger_entry = frappe.get_last_doc('Stock Ledger Entry', filters={'item_code':item})
        avg_cost = stock_ledger_entry.valuation_rate
    return avg_cost


@frappe.whitelist()
def get_price_list_rate(price_list, item):
    price_list_rate = 0
    if frappe.db.exists('Item Price',{'price_list': price_list, 'item_code': item}):
        item_price = frappe.get_last_doc('Item Price',{'price_list': price_list, 'item_code': item})
        price_list_rate = item_price.price_list_rate
    return price_list_rate

@frappe.whitelist()
def get_available_qty(warehouse, item):
    query = """
		select
            SUM(b.actual_qty) as product_stock
		from
            `tabBin` as b
		where
			b.item_code = %(item_code)s AND
			b.warehouse = %(warehouse)s
	"""
    return_data = frappe.db.sql(query.format(), { 'item_code': item, 'warehouse': warehouse }, as_dict=True)
    if return_data and return_data[0].product_stock:
        return return_data[0].product_stock
    else:
        return 0

@frappe.whitelist()
def get_print_format_and_lh(doctype, cost_center):
    defaults = { 'letter_head': "", 'print_format': "" }
    multi_branch_settings = frappe.get_doc('Multi Branch Settings')
    cost_center_defaults = multi_branch_settings.cost_center_defaults
    if cost_center_defaults:
        for cost_center_default in cost_center_defaults:
            if cost_center_default.cost_center == cost_center and cost_center_default.document_type == doctype :
                defaults['print_format'] = cost_center_default.print_format
                defaults['letter_head'] = cost_center_default.letter_head
    return defaults
