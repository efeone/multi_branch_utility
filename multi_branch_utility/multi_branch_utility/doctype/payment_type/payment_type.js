// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Type', {
	refresh: function(frm) {
    if(frm.is_new()){
      frm.set_intro("You're not authorised to create new Payment Type", "red");
      frm.disable_save()
    }
    else{
      if(!frm.doc.payment_type_accounts.length && frm.doc.payment_type!='CREDIT'){
        frm.set_intro("Setup Cost Centers and Mode of Payments", "blue");
      }
    }
		set_filters(frm);
	}
});

let set_filters = function(frm){
	let type = 0
	if(frm.doc.payment_type){
		if (frm.doc.payment_type == 'CASH'){
			type = 'Cash'
		}
		else if (frm.doc.payment_type == 'BANK'){
			type = 'Bank'
		}
		else {
			type=0
		}
		if(type){
			frm.set_query('mode_of_payment', 'payment_type_accounts', function (doc, cdt, cdn) {
				return {
					filters: {
						type: type
					}
				}
			});
		}
	}
}
