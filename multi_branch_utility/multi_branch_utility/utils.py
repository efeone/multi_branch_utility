import frappe
from frappe.utils import *
from frappe import _

@frappe.whitelist()
def get_mode_of_payment(payment_type, cost_center):
    payment_type_details = ''
    payment_type_doc = frappe.get_doc('Payment Type', payment_type )
    if payment_type_doc.payment_type_accounts:
        for payment_type_account in payment_type_doc.payment_type_accounts:
            if payment_type_account.cost_center == cost_center:
                payment_type_details = payment_type_account
    return payment_type_details
