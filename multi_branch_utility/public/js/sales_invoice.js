frappe.ui.form.on('Sales Invoice', {
    onload_post_render(frm) {
        frm.remove_custom_button('Fetch Timesheet')
    },
    on_submit(frm)
    {
      print_invoice(frm.doc)
    },
    refresh(frm){
        frm.set_value('update_stock', 1);
        frm.remove_custom_button('Fetch Timesheet')
        frm.set_query("customer", function() {
    			return {
    				filters: {
    					payment_type: frm.doc.payment_type
    				}
    			};
    		});
    },
    customer: function(frm){
        if(frm.doc.customer){
            frappe.call({
                'method': 'frappe.client.get',
                args: {
                    doctype: 'Customer',
                    name: frm.doc.customer
                },
                callback: function (data) {
                    if(data.message){
                        frm.set_value('payment_type', data.message.payment_type);
                        frm.set_value('set_warehouse', data.message.default_warehouse);
                        frm.set_value('selling_price_list', data.message.default_price_list);
                    }
                }
            });
            frappe.call({
              method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
              args: {
                company: frm.doc.company,
                party_type: 'Customer',
                party: frm.doc.customer,
                date: frm.doc.posting_date,
                cost_center: frm.doc.cost_center
              },
              callback: function(r) {
                if(r.message.party_balance) {
                  frm.set_value('customer_balance', r.message.party_balance)
                }
              }
            });
        }
    },
});

frappe.ui.form.on('Sales Invoice Item', {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn]
        if (frm.doc.customer && row.item_code) {
            frappe.call({
                method: 'multi_branch_utility.multi_branch_utility.utils.get_last_si_rate',
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
                method: 'multi_branch_utility.multi_branch_utility.utils.get_last_pr_rate',
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
                method: 'multi_branch_utility.multi_branch_utility.utils.get_avg_cost',
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
function print_invoice(doc){
  frappe.call({
      method: 'multi_branch_utility.multi_branch_utility.utils.get_print_format_and_lh',
      args: {
          'doctype': doc.doctype,
          'cost_center': doc.cost_center
      },
      callback: function (r) {
          if(r && r.message){
            let defaults = r.message;
            let print_format = "Standard";
            let letter_head = ""
            if(defaults['print_format']){
              print_format = defaults['print_format']
            }
            if(defaults['letter_head']){
              letter_head = defaults['letter_head']
              window.open("/printview?doctype=Sales%20Invoice&name="+ doc.name +"&trigger_print=1&format="+ print_format +"&no_letterhead=0&letterhead="+ letter_head +"&settings=%7B%7D&_lang=en-US")
            }
            else{
              window.open("/printview?doctype=Sales%20Invoice&name="+ doc.name +"&trigger_print=1&format="+ print_format +"&no_letterhead=1&settings=%7B%7D&_lang=en-US")
            }
          }
      }
  })
}
