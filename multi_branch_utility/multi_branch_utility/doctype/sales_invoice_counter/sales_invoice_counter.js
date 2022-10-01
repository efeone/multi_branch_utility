// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'erpnext/selling/sales_common.js' %};
frappe.provide("erpnext.accounts");

erpnext.accounts.SalesInvoiceController = erpnext.selling.SellingController.extend({

});
$.extend(cur_frm.cscript, new erpnext.accounts.SalesInvoiceController({frm: cur_frm}));
frappe.ui.form.on('Sales Invoice Counter', {
	refresh: function(frm) {
		frm.disable_save();
		frm.refresh_fields()
		create_sales_invoice_btn(frm)
	}
});
function create_sales_invoice_btn(frm){
	frm.add_custom_button(__('Submit Invoice'), function(){
		create_invoice(frm)
	}).addClass("btn-primary");
}
function create_invoice(frm){
	if(cur_frm.doc.items.length){
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
		args:{
			'self':doc.name
		},
		callback:function(r){
			if(r){
				frm.reload_doc()
				frappe.show_alert({
					message:__('Invoiced'),
					indicator:'red'
				}, 5);
				window.open("/printview?doctype=Sales%20Invoice&name="+ doc.name +"&trigger_print=1&format=KAS%20VAT%20Invoice%20New&no_letterhead=0&letterhead=Gateway%20Wholesale&settings=%7B%7D&_lang=en-US")
			}
		},
		freeze: true,
	 freeze_message: ('Creating Sales Invoice.!!')
	})
}
