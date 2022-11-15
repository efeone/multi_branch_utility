from . import __version__ as app_version

app_name = "multi_branch_utility"
app_title = "Multi Branch Utility"
app_publisher = "efeone Pvt. Ltd."
app_description = "Frappe application to support Multi Branch setup in ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@efeone.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/multi_branch_utility/css/multi_branch_utility.css"
# app_include_js = "/assets/multi_branch_utility/js/multi_branch_utility.js"

# include js, css files in header of web template
# web_include_css = "/assets/multi_branch_utility/css/multi_branch_utility.css"
# web_include_js = "/assets/multi_branch_utility/js/multi_branch_utility.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "multi_branch_utility/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Payment Entry" : "public/js/payment_entry.js",
	"Sales Invoice" : "public/js/sales_invoice.js",
	"Stock Entry" : "public/js/stock_entry.js",
	"Purchase Invoice" : "public/js/purchase_invoice.js",
	"Item" : "public/js/item.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "multi_branch_utility.install.before_install"
# after_install = "multi_branch_utility.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "multi_branch_utility.uninstall.before_uninstall"
# after_uninstall = "multi_branch_utility.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "multi_branch_utility.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Payment Entry": {
		"on_submit": "multi_branch_utility.multi_branch_utility.doc_events.apply_additional_discount",
	},
	"Sales Invoice": {
		"before_validate": "multi_branch_utility.multi_branch_utility.doc_events.set_import_missing_values",
		"on_submit": "multi_branch_utility.multi_branch_utility.doc_events.make_payment",
		"autoname": "multi_branch_utility.multi_branch_utility.utils.invoice_auto_name"
	},
	"Purchase Invoice": {
		"on_submit": "multi_branch_utility.multi_branch_utility.doc_events.make_payment",
		"autoname": "multi_branch_utility.multi_branch_utility.utils.invoice_auto_name"
	}
}
fixtures = ["Print Format", "Letter Head", "Payment Type"]
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"multi_branch_utility.tasks.all"
# 	],
# 	"daily": [
# 		"multi_branch_utility.tasks.daily"
# 	],
# 	"hourly": [
# 		"multi_branch_utility.tasks.hourly"
# 	],
# 	"weekly": [
# 		"multi_branch_utility.tasks.weekly"
# 	]
# 	"monthly": [
# 		"multi_branch_utility.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "multi_branch_utility.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "multi_branch_utility.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "multi_branch_utility.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"multi_branch_utility.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
