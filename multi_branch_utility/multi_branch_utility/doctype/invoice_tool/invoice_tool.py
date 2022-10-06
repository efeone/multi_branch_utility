# Copyright (c) 2022, efeone Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class InvoiceTool(Document):
	def validate(self):
		frappe.throw(_('No Permision To Save!'))
