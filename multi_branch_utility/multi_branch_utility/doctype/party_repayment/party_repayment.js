// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Party Repayment', {
	refresh(frm) {
		frm.set_query("paid_from", function() {
			frm.events.validate_company(frm);

			var account_types = in_list(["Receive"], frm.doc.payment_type) ?
				["Bank", "Cash"] : [frappe.boot.party_account_types[frm.doc.party_type]];
			return {
				filters: {
					"account_type": ["in", account_types],
					"is_group": 0,
					"company": frm.doc.company
				}
			}
		});
		frm.set_query("paid_to", function() {
			frm.events.validate_company(frm);

			var account_types = in_list(["Pay"], frm.doc.payment_type) ?
				["Bank", "Cash"] : [frappe.boot.party_account_types[frm.doc.party_type]];
			return {
				filters: {
					"account_type": ["in", account_types],
					"is_group": 0,
					"company": frm.doc.company
				}
			}
		});
	},

	validate_company: (frm) => {
		if (!frm.doc.company){
			frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
		}
	},

	mode_of_payment:function(frm){
		if(frm.doc.mode_of_payment){
			get_payment_mode_account(frm, frm.doc.mode_of_payment, function(account){
				if(frm.doc.payment_type == 'Pay'){
					frm.set_value('paid_to', account)
				}
				if(frm.doc.payment_type == 'Receive'){
					frm.set_value('paid_from', account)
				}
			});
		}
		else{
			//clearing account field
			if(frm.doc.payment_type == 'Pay'){
				frm.set_value('paid_to', '')
			}
			if(frm.doc.payment_type == 'Receive'){
				frm.set_value('paid_from', '')
			}
		}
	},

	payment_type: function(frm){
		if(frm.doc.payment_type == 'Pay'){
			frm.set_value("party_type", 'Customer');
		}
		if(frm.doc.payment_type == 'Receive'){
			frm.set_value("party_type", 'Supplier');
		}
	},
	party_type: function(frm) {
		frm.set_query("party", function() {
			if(frm.doc.party_type == 'Customer'){
				return {
					query: "erpnext.controllers.queries.customer_query"
				}
			}
		});
		if(frm.doc.party) {
			$.each(["party", "party_balance", "paid_from", "paid_to",
				"paid_to_account_balance"],
				function(i, field) {
					frm.set_value(field, null);
				})
		}
	},
	party: function(frm) {
		if(frm.doc.payment_type && frm.doc.party_type && frm.doc.party && frm.doc.company) {
			if(!frm.doc.posting_date) {
				frappe.msgprint(__("Please select Posting Date before selecting Party"))
				frm.set_value("party", "");
				return ;
			}
			frm.set_party_account_based_on_party = true;

			let company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;

			return frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
				args: {
					company: frm.doc.company,
					party_type: frm.doc.party_type,
					party: frm.doc.party,
					date: frm.doc.posting_date,
					cost_center: frm.doc.cost_center
				},
				callback: function(r, rt) {
					if(r.message) {
						frappe.run_serially([
							() => {
								if(frm.doc.payment_type == "Pay") {
									frm.set_value("paid_from", r.message.party_account);
									// frm.set_value("paid_from_account_currency", r.message.party_account_currency);
									frm.set_value("paid_from_account_balance", r.message.account_balance);
								} else if (frm.doc.payment_type == "Receive"){
									frm.set_value("paid_to", r.message.party_account);
									// frm.set_value("paid_to_account_currency", r.message.party_account_currency);
									frm.set_value("paid_to_account_balance", r.message.account_balance);
								}
							},
							() => frm.set_value("party_balance", r.message.party_balance),
							() => frm.set_value("party_name", r.message.party_name)
						]);
					}
				}
			});
		}
	},
});

let get_payment_mode_account = function(frm, mode_of_payment, callback) {
	if(!frm.doc.company) {
		frappe.throw(__('Please select the Company first'));
	}
	if(!mode_of_payment) {
		return;
	}
	return  frappe.call({
		method: 'erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account',
		args: {
			'mode_of_payment': mode_of_payment,
			'company': frm.doc.company
		},
		callback: function(r, rt) {
			if(r.message) {
				callback(r.message.account)
			}
		}
	});
}

