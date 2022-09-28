frappe.ui.form.on('Purchase Invoice', {
    
    on_submit(frm)
    {
     window.open("/printview?doctype=Purchase%20Invoice&name="+ frm.doc.name +"&trigger_print=1&format=Standard&no_letterhead=1&settings=%7B%7D&_lang=en-US")
    },
    
});