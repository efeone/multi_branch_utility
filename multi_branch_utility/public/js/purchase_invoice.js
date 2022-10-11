frappe.ui.form.on('Purchase Invoice', {
    on_submit(frm)
    {
     window.open("/printview?doctype=Purchase%20Invoice&name="+ frm.doc.name +"&trigger_print=1&format=Standard&no_letterhead=1&settings=%7B%7D&_lang=en-US")
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
