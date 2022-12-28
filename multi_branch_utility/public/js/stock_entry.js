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


frappe.ui.form.on('Stock Entry Detail', {
s_warehouse:function(frm, cdt, cdn){
	var d = locals[cdt][cdn]
	if(d.s_warehouse && !d.item_code){
		frappe.call({
				'method':'multi_branch_utility.multi_branch_utility.utils.get_cost_center',
				args: {
					'warehouse':d.s_warehouse
				},
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,'cost_center',r.message)
					}
				}
		})
	}

},
t_warehouse:function(frm, cdt, cdn){
	var d = locals[cdt][cdn]
	if(d.t_warehouse && !d.s_warehouse && !d.item_code){
		frappe.call({
				'method':'multi_branch_utility.multi_branch_utility.utils.get_cost_center',
				args: {
					'warehouse':d.t_warehouse
				},
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,'cost_center',r.message)
					}
				}
		})
	}

},
item_code:function(frm, cdt, cdn){
	var d = locals[cdt][cdn]
	if(d.item_code){
		frappe.call({
				'method':'multi_branch_utility.multi_branch_utility.utils.get_item_cost_center',
				args: {
					'item_code':d.item_code
				},
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,'cost_center',r.message)
					}
				}
		})
	}
}
})

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
