// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Salary Component", {
	// setup: function (frm) {
	// 	frm.trigger("reset_component_account_table");
	// },

	type: function (frm) {		
		if (frm.doc.type == "Contribution") {
			frm.set_value("variable_based_on_taxable_salary", 0);
			frm.set_value("is_income_tax_component", 0);
			frm.set_value("exempted_from_income_tax", 0);
			frm.set_value("is_tax_applicable", 0);
			frm.set_value("deduct_full_tax_on_selected_payroll_date", 0);
		}
		// frm.trigger("reset_component_account_table");
		// frm.refresh_fields("accounts");
	},

	// reset_component_account_table: function (frm) {
	// 	let account_fields = [
	// 		{ fieldname: "company", columns: 6 },
	// 		{ fieldname: "account", columns: 4 },
	// 	];

	// 	if (frm.doc.type == "Contribution") {
	// 		account_fields = [
	// 			{ fieldname: "company", columns: 4 },
	// 			{ fieldname: "account", columns: 3 },
	// 			{ fieldname: "custom_bcn_account", columns: 3 },
	// 		];
	// 	} 
		
	// 	frm.get_field("accounts").grid.editable_fields = account_fields		
	// }
});