frappe.ui.form.on('Stock Entry', {
	refresh(frm) {
		ignore_permissions_for_transfer(frm);
		frm.set_query("stock_entry_type", function() {
			return {
				filters: {
					disable: 0,
				}
			};
		});
	},
	stock_entry_type(frm) {
		ignore_permissions_for_transfer(frm);
	}
});

function ignore_permissions_for_transfer(frm){
	if(frm.doc.stock_entry_type && frm.doc.stock_entry_type == 'Material Transfer' ){
		frm.set_df_property('to_warehouse', 'ignore_user_permissions', 1);
		frm.refresh_field('to_warehouse');
	}
	else{
		frm.set_df_property('to_warehouse', 'ignore_user_permissions', 0);
		frm.refresh_field('to_warehouse');
	}
}
