frappe.ui.form.on('Sales Invoice', {
    onload_post_render(frm) {
        frm.remove_custom_button('Fetch Timesheet')
    },
    refresh(frm){
        frm.remove_custom_button('Fetch Timesheet')
        if(frm.doc.docstatus == 1 && frm.doc.outstanding_amount!= 0 && frm.doc.payment_type != 'Credit'){
            frm.add_custom_button('Make Payment',function(){
              make_payment(frm);
            }).addClass("btn-primary");
        }
        frm.set_query("customer", function() {
			return {
				filters: {
					payment_type: frm.doc.payment_type
				}
			};
		});
    },
});


let make_payment = function(frm){
    let d = new frappe.ui.Dialog({
    title: 'Make Payment',
    fields: [
        {
            label: 'Mode of Payment',
            fieldname: 'mode_of_payment',
            fieldtype: 'Link',
            options: 'Mode of Payment',
            reqd: 1,
            read_only:1
        },
        {
            label:"Grand Total",
            fieldname: 'grand_total',
            fieldtype: 'Currency',
            default: frm.doc.outstanding_amount,
            read_only: 1
        },
        {
            label:"Recieved Amount",
            fieldname: 'recieved_amount',
            fieldtype: 'Currency',
            reqd: 1,
            default: frm.doc.outstanding_amount
        },
        {
            label:"Cheque/Reference No",
            fieldname: 'reference_no',
            fieldtype: 'Data'
        },
        {
            label:"Cheque/Reference Date",
            fieldname: 'reference_date',
            fieldtype: 'Date'
        }
    ],
    primary_action_label: 'Submit',
    primary_action(values) {
        d.hide();
        if(values.mode_of_payment && values.recieved_amount){
          if(values.recieved_amount > values.grand_total){
            frappe.throw(__("Recieved Amount can't be greater than Grand Total"));
          }
          get_payment_mode_account(frm, values.mode_of_payment, function(account){
            frappe.call({
              method: 'multi_branch_utility.multi_branch_utility.doc_events.make_payment',
              args: {
                'sales_invoice': frm.doc.name,
                'mode_of_payment': values.mode_of_payment,
                'paid_amount': values.recieved_amount,
                'account_paid_to': account,
                'reference_no': values.reference_no,
                'reference_date': values.reference_date,
              },
              callback: function(r) {
                if(r) {
                    frm.reload_doc()
                }
              }
            })
          });
        }
        else{
          frappe.throw(__('Mode of Payment and Amount is mandaory'));
        }
    }
    });
    d.set_value('mode_of_payment', frm.doc.payment_type)
    d.show();
}

frappe.ui.form.on('Sales Invoice Item', {
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
                    frm.refresh_field('items');
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
    }
});