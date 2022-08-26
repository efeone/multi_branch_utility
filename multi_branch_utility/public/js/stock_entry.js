frappe.ui.form.on('Stock Entry', {
	refresh(frm) {
		frm.set_query("stock_entry_type", function() {
			return {
				filters: {
					disable: 0,
				}
			};
		});
	}
});