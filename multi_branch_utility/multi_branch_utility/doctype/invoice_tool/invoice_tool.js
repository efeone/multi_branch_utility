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
    calculate_totals(frm)
  },
  item_code: function (frm, cdt, cdn) {
      var row = locals[cdt][cdn]
      if (frm.doc.selling_price_list && row.item_code) {
        frappe.call({
            method: 'multi_branch_utility.multi_branch_utility.utils.get_price_list_rate',
            args: {
                'price_list': frm.doc.selling_price_list,
                'item': row.item_code
            },
            callback: function (r) {
                row.rate = r.message
                frm.refresh_field('items');
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

function make_buttons(frm){
  frm.add_custom_button('Clear form', () => {
    frm.reload_doc();
  }).addClass("btn btn-danger");

  frm.add_custom_button('Create Invoice', () => {
    if ( check_mandatory_fields(frm)){
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
			payment_type:frm.doc.payment_type,
			items: frm.doc.items,
			docstatus: 0
		}).then(function(doc) {
			frappe.show_alert('Sales Invoice Created..', 5);
		});
}

function check_mandatory_fields(frm){
  if (!frm.doc.customer) { frappe.throw(__('Customer is Required!')); }
  if (!frm.doc.posting_date) { frappe.throw(__('Posting Date is Required!')); }
  if (!frm.doc.cost_center) { frappe.throw(__('Cost Center is Required!')); }
  if (!frm.doc.currency) { frappe.throw(__('Currency is Required!')); }
  if (!frm.doc.selling_price_list) { frappe.throw(__('Selling Price List is Required!')); }
  if (!frm.doc.set_warehouse) { frappe.throw(__('Source Warehouse is Required!')); }
  if (!frm.doc.items.length) { frappe.throw(__('Items is Required!')); }
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
  frm.set_value('outstanding_amount', total_amount);
}
