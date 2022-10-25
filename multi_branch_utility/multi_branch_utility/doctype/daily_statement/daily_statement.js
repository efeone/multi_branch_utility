// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Statement', {
	refresh: function(frm) {
    frm.disable_save();
    make_dashboard(frm);
	},
	date: function(frm){
		make_dashboard(frm);
	},
	cost_center: function(frm){
		make_dashboard(frm);
	}
});

function make_dashboard(frm){
	if(frm.doc.cost_center && frm.doc.date){
		frappe.call({
			method: "multi_branch_utility.multi_branch_utility.doctype.daily_statement.daily_statement.get_daily_statement_values",
			args: {
				'cost_center': frm.doc.cost_center,
				'posting_date': frm.doc.date
			},
			callback: function(r) {
				if(r&&r.message){
					$(frm.fields_dict['daily_statement_dashboard'].wrapper).html(r.message);
				}
			}
		});
	}
	else {
		frappe.call({
			method: "multi_branch_utility.multi_branch_utility.doctype.daily_statement.daily_statement.get_html_content",
			args: {
				'template_path': 'templates/nothing_to_show.html'
			},
			callback: function(r) {
				if(r&&r.message){
					$(frm.fields_dict['daily_statement_dashboard'].wrapper).html(r.message);
				}
			}
		});
	}
}
