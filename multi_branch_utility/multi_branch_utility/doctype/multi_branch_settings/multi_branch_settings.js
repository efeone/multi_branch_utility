// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi Branch Settings', {
	refresh: function(frm) {
		frm.set_query("print_format", "cost_center_defaults", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					"doc_type": row.document_type
				}
			}
		});
	}
});
