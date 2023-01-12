frappe.ui.form.on('Customer', {
	tax_id: function(frm) {
		if(isNaN(frm.doc.tax_id) || frm.doc.tax_id.toString().length > 15 ){
			frm.set_value('tax_id', '');
			frm.refresh_field('tax_id');
			frappe.throw(__('Tax Id is Invalid!'))
		}
	}
})
