// Copyright (c) 2022, efeone Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice Tool', {
  refresh: function(frm) {
    frm.set_value('payment_type','CASH');
    frm.disable_save();
    make_buttons(frm);
    frm.set_query("customer", function() {
      return {
        filters: {
          payment_type: frm.doc.payment_type
        }
      };
    });
	},
  cost_center: function(frm){
    if(frm.doc.cost_center){
      frm.doc.items.forEach(function(item){
        item.cost_center = frm.doc.cost_center;
      });
      frm.refresh_field('items');
    }
  },
  set_warehouse: function(frm){
    if(frm.doc.set_warehouse){
      frm.doc.items.forEach(function(item){
        item.warehouse = frm.doc.set_warehouse;
      });
      frm.refresh_field('items');
    }
  },
  customer: function(frm){
    frm.add_child('items');
    frm.refresh_field('items');
    if(frm.doc.customer && frm.doc.company && frm.doc.payment_type == 'CREDIT') {
      if(!frm.doc.posting_date) {
        frappe.msgprint(__("Please select Posting Date before selecting Customer"))
        frm.set_value("customer", "");
        return ;
      }
      return frappe.call({
        method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
        args: {
          company: frm.doc.company,
          party_type: 'Customer',
          party: frm.doc.customer,
          date: frm.doc.posting_date,
          cost_center: frm.doc.cost_center
        },
        callback: function(r) {
          if(r.message.party_balance < 0) {
              frm.set_value('customer_balance', r.message.party_balance)
              frm.set_value('allocate_advances_automatically', 1)
          }
        }
      });
    }
  }
});

frappe.ui.form.on('Invoice Tool Item', {
  items_add: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if(frm.doc.cost_center) {
      row.cost_center = frm.doc.cost_center;
      frm.refresh_field('items');
    }
    if(frm.doc.set_warehouse) {
      row.warehouse = frm.doc.set_warehouse;
      frm.refresh_field('items');
    }
    calculate_totals(frm);
  },
  item_code: function (frm, cdt, cdn) {
      var row = locals[cdt][cdn];
      if (!frm.doc.customer) {
        frm.clear_table('items');
        frm.refresh_field('items');
        frappe.throw(__('Customer is Required!'));
      }
      if (!frm.doc.set_warehouse) {
        frm.clear_table('items');
        frm.refresh_field('items');
        frappe.throw(__('Source Warehouse is Required!'));
      }
      if (frm.doc.selling_price_list && row.item_code) {
        frappe.call({
            method: 'multi_branch_utility.multi_branch_utility.utils.get_price_list_rate',
            args: {
                'price_list': frm.doc.selling_price_list,
                'item': row.item_code
            },
            callback: function (r) {
                row.rate = r.message;
            }
        });
      }
      if (frm.doc.set_warehouse && row.item_code) {
        frappe.call({
            method: 'multi_branch_utility.multi_branch_utility.utils.get_available_qty',
            args: {
                'warehouse': frm.doc.set_warehouse,
                'item': row.item_code
            },
            callback: function (r) {
                row.actual_qty = r.message;
            }
        });
      }
      if (frm.doc.customer && row.item_code) {
          frappe.call({
              method: 'multi_branch_utility.multi_branch_utility.utils.get_last_si_rate',
              args: {
                  'customer': frm.doc.customer,
                  'item': row.item_code
              },
              callback: function (r) {
                  row.previous_selling_rate = r.message;
              }
          });
          frappe.call({
              method: 'multi_branch_utility.multi_branch_utility.utils.get_last_pr_rate',
              args: {
                  'item': row.item_code
              },
              callback: function (r) {
                  row.previous_buying_rate = r.message;
              }
          });
          frappe.call({
              method: 'multi_branch_utility.multi_branch_utility.utils.get_avg_cost',
              args: {
                  'item': row.item_code
              },
              callback: function (r) {
                  row.average_cost = r.message;
              }
          });
      }
      frm.refresh_field('items');
  },
  qty: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if(row.qty) {
      row.amount = row.qty * row.rate ;
    }
    frm.refresh_field('items');
    calculate_totals(frm)
  },
  rate: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if(row.qty) {
      row.amount = row.qty * row.rate ;
    }
    frm.refresh_field('items');
    calculate_totals(frm)
  },
  items_remove: function(frm, cdt, cdn){
    calculate_totals(frm);
  }
});

frappe.ui.keys.on("ctrl+s", function(frm) {
  console.log("Saving via Keyboard Shortcut");
  if (check_mandatory_fields(cur_frm)){
    remove_blank_rows(cur_frm);
    frappe.confirm('Are you sure you want to Approve?',
      (yes) => {
        create_sales_invoice(cur_frm);
      },(no) => {

    });
  }
});

function make_buttons(frm){
  frm.add_custom_button('Goto Sales Invoice', () => {
    frappe.set_route('List', 'Sales Invoice' );
  }).addClass("btn btn-primary");
  frm.add_custom_button('Clear form', () => {
    frm.reload_doc();
  }).addClass("btn btn-danger");

  frm.add_custom_button('Create Invoice', () => {
    if ( check_mandatory_fields(frm)){
      remove_blank_rows(frm);
      frappe.confirm('Are you sure you want to Approve?',
        (yes) => {
          create_sales_invoice(frm);
        },(no) => {

      });
    }
  }).addClass("btn btn-primary");
}

function create_sales_invoice(frm){
  frappe.db.insert({
			doctype: 'Sales Invoice',
			customer: frm.doc.customer,
			payment_type: frm.doc.payment_type,
      update_stock: frm.doc.update_stock,
      outstanding_amount: frm.doc.outstanding_amount,
      total: frm.doc.total,
      grand_total: frm.doc.grand_total,
      rounded_total: frm.doc.rounded_total,
      rounding_adjustment: frm.doc.rounding_adjustment,
			items: frm.doc.items,
			docstatus: 1,
      allocate_advances_automatically: frm.doc.allocate_advances_automatically
		}).then(function(doc) {
			frappe.show_alert('Sales Invoice Created..', 5);
      print_invoice(doc)
      frm.reload_doc();
		});
}

function check_mandatory_fields(frm){
  if (!frm.doc.customer) { frappe.throw(__('Customer is Required!')); }
  if (!frm.doc.posting_date) { frappe.throw(__('Posting Date is Required!')); }
  if (!frm.doc.cost_center) { frappe.throw(__('Cost Center is Required!')); }
  if (!frm.doc.selling_price_list) { frappe.throw(__('Selling Price List is Required!')); }
  if (!frm.doc.set_warehouse) { frappe.throw(__('Source Warehouse is Required!')); }
  if (!frm.doc.items.length) { frappe.throw(__('Item is Required!')); }
  return 1
}

function calculate_totals(frm){
  var total_qty = 0;
  var total_amount = 0;
  frm.doc.items.forEach(function(item){
    if (item.amount){
      total_amount = total_amount + item.amount;
    }
    if(item.qty){
      total_qty = total_qty + item.qty;
    }
  });
  frm.set_value('total_qty', total_qty);
  frm.set_value('total', total_amount);
  frm.set_value('grand_total', total_amount);
  frm.set_value('rounded_total', Math.round(total_amount));
  frm.set_value('rounding_adjustment', frm.doc.rounded_total - frm.doc.grand_total );
  frm.set_value('outstanding_amount', frm.doc.rounded_total);
}

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

function remove_blank_rows(frm){
  let len = frm.doc.items.length;
  if(!frm.doc.items[len-1].item_code && len>1){
    frm.get_field('items').grid.grid_rows[len-1].remove();
    frm.refresh_field('items');
  }
}
