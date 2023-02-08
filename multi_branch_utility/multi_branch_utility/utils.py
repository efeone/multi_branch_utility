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
    last_si_rate = 0
    query = '''
        SELECT
            sii.rate as last_si_rate
        FROM
            `tabSales Invoice` as si,
            `tabSales Invoice Item` as sii
        WHERE
            si.customer = %(customer)s
            AND si.docstatus = 1
            AND sii.parent = si.name
            AND sii.item_code = %(item)s
        ORDER BY
            si.creation desc
    '''
    return_data = frappe.db.sql(query.format(), { 'customer':customer, 'item':item}, as_dict = True)
    if return_data:
        last_si_rate = return_data[0].get('last_si_rate')
    return last_si_rate

@frappe.whitelist()
def get_last_pr_rate(item):
    last_pr_rate = 0
    query = '''
        SELECT
            pri.rate as last_pr_rate
        FROM
            `tabPurchase Receipt` as pr,
            `tabPurchase Receipt Item` as pri
        WHERE
            pr.docstatus = 1
            AND pri.item_code = %(item)s
            AND pri.parent = pr.name
        ORDER BY
            pr.creation desc
    '''
    return_data = frappe.db.sql(query.format(), { 'item':item }, as_dict = True)
    if return_data:
        last_pr_rate = return_data[0].get('last_pr_rate')
    return last_pr_rate

@frappe.whitelist()
def get_avg_cost(item):
    avg_cost = 0
    query = '''
        SELECT
            sle.valuation_rate as avg_cost
        FROM
            `tabStock Ledger Entry` as sle
        WHERE
            sle.item_code = %(item)s
        ORDER BY
            creation desc
    '''
    return_data = frappe.db.sql(query.format(), { 'item':item }, as_dict = True)
    if return_data:
        avg_cost = return_data[0].get('avg_cost')
    return avg_cost

@frappe.whitelist()
def get_price_list_rate(price_list, item):
    price_list_rate = 0
    query = '''
    SELECT
        ip.price_list_rate as price_list_rate
    FROM
        `tabItem Price` as ip
    WHERE
        ip.price_list = %(price_list)s
        AND ip.item_code = %(item)s
    ORDER BY
        creation desc
    '''
    return_data = frappe.db.sql(query.format(),{ 'price_list':price_list, 'item':item }, as_dict = True)
    if return_data:
        price_list_rate = return_data[0].get('price_list_rate')
    return price_list_rate

@frappe.whitelist()
def get_available_qty(warehouse, item):
    query = """
		SELECT
            SUM(b.actual_qty) as product_stock
		FROM
            `tabBin` as b
		WHERE
			b.item_code = %(item_code)s
            AND b.warehouse = %(warehouse)s
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

@frappe.whitelist()
def invoice_auto_name(doc, method):
    from frappe.model.naming import make_autoname
    multi_branch_settings = frappe.get_doc('Multi Branch Settings')
    cost_center_defaults = multi_branch_settings.cost_center_defaults
    if cost_center_defaults:
        for cost_center_default in cost_center_defaults:
            if cost_center_default.cost_center == doc.cost_center and cost_center_default.document_type == doc.doctype:
                invoice_series = cost_center_default.invoice_series
                doc.name = make_autoname(invoice_series)

@frappe.whitelist()
def get_cost_center(warehouse):
    warehouse_doc = frappe.get_doc("Warehouse",warehouse)
    return  warehouse_doc.cost_center

@frappe.whitelist()
def get_item_cost_center(item_code):
    item_doc = frappe.get_doc("Item",item_code)
    return  item_doc.cost_center

@frappe.whitelist()
def set_payment_types():
    payment_types = ['CREDIT', 'BANK', 'CASH']
    for payment_type in payment_types:
        if not frappe.db.exists('Payment Type', payment_type):
            doc = frappe.new_doc('Payment Type')
            doc.payment_type = payment_type
            doc.save()

@frappe.whitelist()
def get_item_details(customer, item, price_list, warehouse):
    item_details = { 'price_list_rate':0, 'available_qty':0, 'avg_cost':0, 'last_si_rate':0, 'last_pr_rate':0 }
    item_details['last_si_rate'] = get_last_si_rate(customer, item)
    item_details['last_pr_rate'] = get_last_pr_rate(item)
    item_details['avg_cost'] = get_avg_cost(item)
    item_details['price_list_rate'] = get_price_list_rate(price_list, item)
    item_details['available_qty'] = get_available_qty(warehouse, item)
    return item_details
