// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'erpnext/selling/sales_common.js' %};
frappe.provide("erpnext.accounts");
erpnext.accounts.SalesInvoiceController = erpnext.selling.SellingController.extend({
});
$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));
frappe.ui.form.on('Sales Invoice Counter', {
	refresh: function(frm) {
		$(".grid-add-multiple-rows").hide()
		frm.disable_save();
		frm.refresh_fields()
		create_sales_invoice_btn(frm)
		list_sales_invoice_btn(frm)
	}
});
frappe.ui.form.on('Sales Invoice Counter Item', {
	price_list_rate:function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		frappe.model.set_value(row.doctype,row.name,'qty',0)
	},
	item_code: function (frm, cdt, cdn) {
			var row = locals[cdt][cdn]
			if (frm.doc.customer && row.item_code) {
					frappe.call({
							method: 'multi_branch_utility.multi_branch_utility.doc_events.get_last_si_rate',
							args: {
									'customer': frm.doc.customer,
									'item': row.item_code
							},
							callback: function (r) {
									let prev_si_rate = r.message
									row.previous_selling_rate = prev_si_rate
							}
					})
					frappe.call({
							method: 'multi_branch_utility.multi_branch_utility.doc_events.get_last_pr_rate',
							args: {
									'item': row.item_code
							},
							callback: function (r) {
									let prev_pr_rate = r.message
									row.previous_buying_rate = prev_pr_rate
									frm.refresh_field('items');
							}
					})
					frappe.call({
							method: 'multi_branch_utility.multi_branch_utility.doc_events.get_avg_cost',
							args: {
									'item': row.item_code
							},
							callback: function (r) {
									let avg_cost = r.message
									row.average_cost = avg_cost
									frm.refresh_field('items');
							}
					})
			}
	},
	items_remove:function(frm,cdt,cdn){
		console.log("eee");
		var total_amount = 0
		var total_qty = 0
		frm.doc.items.forEach(function(item){
			total_amount +=item.amount
			total_qty +=item.qty
		})
		frm.set_value('total',total_amount)
		frm.set_value('total_qty',total_qty)
		frm.set_value('grand_total',total_amount)
		frm.set_value('rounded_total',total_amount)
	},
	});
	function create_sales_invoice_btn(frm){
	frm.add_custom_button(__('Submit Invoice'), function(){
		create_invoice(frm)
	}).addClass("btn-primary");
	}
	function create_invoice(frm){
	if(frm.doc.items.length){
		frappe.db.insert({
			doctype: 'Sales Invoice',
			customer: frm.doc.customer,
			payment_type:frm.doc.payment_type,
			items: frm.doc.items,
			docstatus:1
		}).then(function(doc) {
			make_payment(frm,doc)
		});
	}else{
		frappe.msgprint({
			title: __('Notification'),
			indicator: 'red',
			message: __('Select Item')
		});
	}

	}
	function make_payment(frm,doc){
	frappe.call({
		method:'multi_branch_utility.multi_branch_utility.doctype.sales_invoice_counter.sales_invoice_counter.make_payment',
		freeze: true,
	 freeze_message: ('Creating Sales Invoice.!!'),
		args:{
			'self':doc.name
		},
		callback:function(r){
			if(r){
				frappe.show_alert({
					message:__('Invoiced'),
					indicator:'red'
				}, 5);
				frm.reload_doc()
				window.open("/printview?doctype=Sales%20Invoice&name="+ doc.name +"&trigger_print=1&format=KAS%20VAT%20Invoice%20New&no_letterhead=0&letterhead=Gateway%20Wholesale&settings=%7B%7D&_lang=en-US")
			}
		},
	})
	}

	function list_sales_invoice_btn(frm){
	frm.add_custom_button(__('List Invoice'), function(){
		list_invoice(frm)
	}).addClass("btn-success");
	}

	function list_invoice(frm){
	frappe.set_route("List", "Sales Invoice");
	}
