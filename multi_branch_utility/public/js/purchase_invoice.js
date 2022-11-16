frappe.ui.form.on('Purchase Invoice', {
  refresh(frm){
  frm.set_value('update_stock', 1);
  },
  on_submit(frm)
  {
      print_invoice(frm.doc)
  },
  supplier: function(frm){
    if(frm.doc.supplier){
        frappe.call({
            'method': 'frappe.client.get',
            args: {
                doctype: 'Supplier',
                name: frm.doc.supplier
            },
            callback: function (data) {
                if(data.message){
                    frm.set_value('payment_type', data.message.payment_type)
                    frm.set_value('set_warehouse', data.message.default_warehouse)
                    frm.set_value('buying_price_list', data.message.default_price_list)
                    frm.refresh_fields()
                }
            }
        })
    }
  },
});

let unset_mode_of_payment = function(frm){
  frm.set_value('mode_of_payment', );
  frm.refresh_field('mode_of_payment');
  frm.set_value('mode_of_payment_account', );
  frm.refresh_field('mode_of_payment_account');
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
              window.open("/printview?doctype=Purchase%20Invoice&name="+ doc.name +"&trigger_print=1&format="+ print_format +"&no_letterhead=0&letterhead="+ letter_head +"&settings=%7B%7D&_lang=en-US")
            }
            else{
              window.open("/printview?doctype=Purchase%20Invoice&name="+ doc.name +"&trigger_print=1&format="+ print_format +"&no_letterhead=1&settings=%7B%7D&_lang=en-US")
            }
          }
      }
  })
}
