import frappe
import erpnext
from frappe import _, bold, throw
from frappe.model.document import Document
from datetime import date,datetime
from frappe.utils import *
from erpnext.accounts.party import get_party_account
from multi_branch_utility.multi_branch_utility.utils import get_print_format_and_lh

@frappe.whitelist()
def apply_additional_discount(doc, method):
	if doc.additional_discount_account and doc.additional_discount_amount:
		discount_amount = doc.additional_discount_amount
		for ref in doc.references:
			if ref.outstanding_amount > 0 and discount_amount > 0:
				allocated_amount = 0
				if ref.outstanding_amount == discount_amount:
					allocated_amount = ref.outstanding_amount
				elif ref.outstanding_amount < discount_amount:
					allocated_amount = discount_amount - ref.outstanding_amount
				elif ref.outstanding_amount > discount_amount:
					allocated_amount = ref.outstanding_amount - discount_amount
				journal_entry = frappe.new_doc('Journal Entry')
				journal_entry.voucher_type = 'Journal Entry'
				journal_entry.company = doc.company
				journal_entry.posting_date =  doc.posting_date
				party_type = 'Customer'
				party_account = get_party_account(party_type, doc.party, doc.company)
				accounts = []
				accounts.append({
						'account': party_account,
						'credit_in_account_currency': allocated_amount,
						'party_type': 'Customer',
						'party': doc.party,
						'reference_type':ref.reference_doctype,
						'reference_name': ref.reference_name
					}
				)
				accounts.append({
					'account': doc.additional_discount_account,
					'debit_in_account_currency': allocated_amount,
					'party_type': 'Customer',
					'party': doc.party
				})
				journal_entry.set('accounts', accounts)
				journal_entry.save(ignore_permissions = True)
				journal_entry.submit()
				discount_amount = discount_amount - allocated_amount

@frappe.whitelist()
def set_import_missing_values(doc, method):
	if doc.items:
		for item in doc.items:
			if not item.income_account:
				item.income_account = frappe.get_cached_value("Company", doc.company, "default_income_account")
				item.description = item.item_name
	if not doc.cost_center:
		doc.cost_center = frappe.get_cached_value("Customer", doc.customer, "cost_center")

@frappe.whitelist()
def make_payment(doc, method):
	if frappe.db.get_single_value('Multi Branch Settings', 'allow_payment_entry'):
		if doc.payment_type == 'CASH':
			from multi_branch_utility.multi_branch_utility.utils import get_mode_of_payment
			payment_type_details = get_mode_of_payment(doc.payment_type, doc.cost_center)
			if not payment_type_details:
				frappe.throw('Please set Mode of Payment in Payment Type CASH')
			if payment_type_details:
				if not doc.is_return and doc.payment_type and doc.payment_type == 'CASH' and payment_type_details.mode_of_payment and payment_type_details.account:
					company = frappe.get_last_doc('Company')
					if doc.doctype == "Sales Invoice":
						reference_doctype = doc.doctype
						party_type = "Customer"
						party = doc.customer
						paid_to = payment_type_details.account
						paid_from =  get_party_account(party_type, party, company.name)
						payment_type = "Receive"
					if doc.doctype == "Purchase Invoice":
						reference_doctype = doc.doctype
						party_type = "Supplier"
						party = doc.supplier
						paid_from = payment_type_details.account
						paid_to =  get_party_account(party_type, party, company.name)
						payment_type = "Pay"
					pay = frappe.new_doc('Payment Entry')
					pay.payment_type = payment_type
					pay.mode_of_payment = payment_type_details.mode_of_payment
					pay.posting_date = doc.posting_date
					pay.party_type = party_type
					pay.party = party
					pay.paid_from = paid_from
					pay.source_exchange_rate = 1
					pay.paid_amount = doc.outstanding_amount
					pay.received_amount = doc.outstanding_amount
					pay.paid_to = paid_to
					pay.cost_center = doc.cost_center
					pay.append("references",{
						"reference_doctype" : reference_doctype,
						"reference_name": doc.name,
						"total_amount": doc.grand_total,
						"outstanding_amount": doc.outstanding_amount,
						"allocated_amount": doc.outstanding_amount
					})
					pay.submit()
					frappe.msgprint(msg='Payment Enrty against '+ doc.name + ' is completed', title='Message', alert="True")
					doc.reload()

@frappe.whitelist()
def stock_entry_before_validate(doc, method):
	for item in doc.items:
		if item.item_code:
			item_doc = frappe.get_doc('Item', item.item_code)
			if item_doc.cost_center:
				item.cost_center = item_doc.cost_center
			elif item.s_warehouse:
				warehouse = frappe.get_doc('Warehouse', item.s_warehouse)
				if warehouse.cost_center:
					item.cost_center = warehouse.cost_center
			elif item.t_warehouse:
				warehouse = frappe.get_doc('Warehouse', item.t_warehouse)
				if warehouse.cost_center:
					item.cost_center = warehouse.cost_center

@frappe.whitelist()
def sales_invoice_validate(doc, method):
	validate_selling_price(doc)
	if doc.cost_center:
		defaults = get_print_format_and_lh(doc.doctype, doc.cost_center)
		if defaults['letter_head']:
			doc.letter_head = defaults['letter_head']

@frappe.whitelist()
def customer_validate(doc, method):
	''' Method to validate Customer'''
	if doc.tax_id:
		is_num = doc.tax_id.isnumeric() #To check wether it is number or not
		if not is_num or len(doc.tax_id)!=15: #Validating length of tax id
			frappe.throw('Tax Id should have 15 digits number only.')


@frappe.whitelist()
def validate_selling_price(self):
	def throw_message(idx, item_name, rate, ref_rate_field):
		throw(
			_(
				"""Row #{0}: Selling rate for item {1} is lower than its {2}.
				Selling {3} should be atleast {4}.<br><br>Alternatively,
				you can disable selling price validation in {5} to bypass
				this validation."""
			).format(
				idx,
				bold(item_name),
				bold(ref_rate_field),
				bold("net rate"),
				bold(rate),
				bold(self.name),
			),
			title=_("Invalid Selling Price"),
		)

	if self.get("is_return") or self.get("allow_loss_sales") or not frappe.db.get_single_value("Selling Settings", "validate_selling_price"):
		return

	is_internal_customer = self.get("is_internal_customer")
	valuation_rate_map = {}

	for item in self.items:
		if not item.item_code or item.is_free_item:
			continue

		last_purchase_rate, is_stock_item = frappe.get_cached_value(
			"Item", item.item_code, ("last_purchase_rate", "is_stock_item")
		)

		last_purchase_rate_in_sales_uom = last_purchase_rate * (item.conversion_factor or 1)

		if flt(item.base_net_rate) < flt(last_purchase_rate_in_sales_uom):
			throw_message(item.idx, item.item_name, last_purchase_rate_in_sales_uom, "last purchase rate")

		if is_internal_customer or not is_stock_item:
			continue

		valuation_rate_map[(item.item_code, item.warehouse)] = None

	if not valuation_rate_map:
		return

	or_conditions = (
		f"""(item_code = {frappe.db.escape(valuation_rate[0])}
		and warehouse = {frappe.db.escape(valuation_rate[1])})"""
		for valuation_rate in valuation_rate_map
	)

	valuation_rates = frappe.db.sql(
		f"""
		select
			item_code, warehouse, valuation_rate
		from
			`tabBin`
		where
			({" or ".join(or_conditions)})
			and valuation_rate > 0
	""",
		as_dict=True,
	)

	for rate in valuation_rates:
		valuation_rate_map[(rate.item_code, rate.warehouse)] = rate.valuation_rate

	for item in self.items:
		if not item.item_code or item.is_free_item:
			continue

		last_valuation_rate = valuation_rate_map.get((item.item_code, item.warehouse))

		if not last_valuation_rate:
			continue

		last_valuation_rate_in_sales_uom = last_valuation_rate * (item.conversion_factor or 1)

		if flt(item.base_net_rate) < flt(last_valuation_rate_in_sales_uom):
			throw_message(item.idx, item.item_name, last_valuation_rate_in_sales_uom, "valuation rate")
