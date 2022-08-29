frappe.ui.form.on('Sales Invoice', {
    onload_post_render(frm) {
        frm.remove_custom_button('Fetch Timesheet')
    }
});

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