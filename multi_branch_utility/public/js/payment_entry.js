frappe.ui.form.on('Payment Entry', {
	refresh(frm) {
		frm.set_query("additional_discount_account", function() {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					report_type: "Profit and Loss",
				}
			};
		});
	}
});