frappe.ui.form.on('Purchase Invoice', {
    on_submit(frm)
    {
     window.open("/printview?doctype=Purchase%20Invoice&name="+ frm.doc.name +"&trigger_print=1&format=Standard&no_letterhead=1&settings=%7B%7D&_lang=en-US")
    },
    payment_type(frm){
      if(frm.doc.payment_type && frm.doc.cost_center){
        frappe.call({
            method: 'multi_branch_utility.multi_branch_utility.utils.get_mode_of_payment',
            args: {
              'payment_type': frm.doc.payment_type,
              'cost_center' : frm.doc.cost_center
            },
            callback: function (r) {
              if( r && r.message ){
                frm.set_value('mode_of_payment', r.message.mode_of_payment);
                frm.refresh_field('mode_of_payment');
                frm.set_value('mode_of_payment_account', r.message.account);
                frm.refresh_field('mode_of_payment_account');
              }
              else{
                unset_mode_of_payment(frm)
              }
            }
        });
      }
      else{
        unset_mode_of_payment(frm)
      }
    }
});

let unset_mode_of_payment = function(frm){
  frm.set_value('mode_of_payment', );
  frm.refresh_field('mode_of_payment');
  frm.set_value('mode_of_payment_account', );
  frm.refresh_field('mode_of_payment_account');
}
