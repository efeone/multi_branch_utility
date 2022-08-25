frappe.ui.form.on('Sales Invoice', {
    onload_post_render(frm) {
        frm.remove_custom_button('Fetch Timesheet')
    }
});