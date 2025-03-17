// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Salary Slip", {
    setup: function (frm) {
		frm.get_field("custom_bcn_contributions").grid.editable_fields = [
			{ fieldname: "salary_component", columns: 6 },
			{ fieldname: "amount", columns: 4 },
		];

        frm.set_query("salary_component", "custom_bcn_contributions", function () {
			return {
				filters: {
					type: "contribution",
				},
			};
		});
    },	
});

// frappe.ui.form.on("BCN Contribution Detail", {
// 	salary_component: function (frm, cdt, cdn) {
// 		var child = locals[cdt][cdn];
// 		if (child.salary_component) {
// 			frappe.call({
// 				method: "frappe.client.get",
// 				args: {
// 					doctype: "Salary Component",
// 					name: child.salary_component,
// 				},
// 				callback: function (data) {
// 					if (data.message) {
// 						var result = data.message;
						
// 						frappe.model.set_value(
// 							cdt,
// 							cdn,
// 							"is_one_time_contribution",
// 							result.custom_bcn_is_one_time_contribution,
// 						);						
// 						refresh_field("custom_bcn_contributions");
// 					}
// 				},
// 			});
// 		}
// 	},
// });