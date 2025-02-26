// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Salary Structure", {
    onload: function() {
        frm.trigger("set_contributions_component");
    },
    refresh: function (frm) {
        frm.trigger("set_contributions_component");
    },
    company: function (frm) {
		frm.trigger("set_contributions_component");
	},
    set_contributions_component: function (frm) {
		if (!frm.doc.company) return;		
		frm.set_query("salary_component", "custom_bcn_contributions", function () {
			return {
				filters: { component_type: "contribution", company: frm.doc.company },
				query: "hrms.payroll.doctype.salary_structure.salary_structure.get_salary_component",
			};
		});
	},
});