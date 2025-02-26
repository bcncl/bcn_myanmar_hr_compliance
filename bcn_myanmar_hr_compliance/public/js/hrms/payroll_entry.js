// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Payroll Entry", {
    onload: function (frm) {
        frm.set_query("custom_bcn_contribution_expense_account", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    root_type: "Expense",
                    is_group: 0,
                },
            };
        });
    },
    company: function (frm) {
        frm.events.set_contribution_expense_account(frm);
    },
    set_contribution_expense_account: function (frm) {        
        frappe.db.get_value(
            "Company",
            { name: frm.doc.company },
            "custom_bcn_default_contribution_expense_account",
            (r) => {
                frm.set_value("custom_bcn_contribution_expense_account", r.custom_bcn_default_contribution_expense_account);
            },
        );
    },
});