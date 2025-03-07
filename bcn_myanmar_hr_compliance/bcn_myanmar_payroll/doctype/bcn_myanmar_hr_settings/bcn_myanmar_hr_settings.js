// Copyright (c) 2025, Business Centric Network Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("BCN Myanmar HR Settings", {
	refresh(frm) {
        frm.trigger("set_queries");
	},

    set_queries: function (frm) {
        frm.set_query("component", "default_earnings", function () {
			return {
				filters: { type: "Earning" }
			};
		});

        frm.set_query("component", "default_deductions", function () {
			return {
				filters: { type: "Deduction" }
			};
		});

        frm.set_query("component", "default_contributions", function () {
			return {
				filters: { type: "Contribution" }
			};
		});
    },     
});
