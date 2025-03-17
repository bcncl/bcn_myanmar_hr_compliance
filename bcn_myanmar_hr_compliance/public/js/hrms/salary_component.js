// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Salary Component", {
	type: function (frm) {		
		if (frm.doc.type == "Contribution") {
			frm.set_value("variable_based_on_taxable_salary", 0);
			frm.set_value("depends_on_payment_days", 0);
			frm.set_value("is_income_tax_component", 0);
			frm.set_value("exempted_from_income_tax", 0);
			frm.set_value("is_tax_applicable", 0);
			frm.set_value("deduct_full_tax_on_selected_payroll_date", 0);

			frm.set_df_property('depends_on_payment_days', 'hidden', 1);
		}
	},
	custom_bcn_is_myanmar_ssc: function (frm) {
		if (frm.doc.custom_bcn_is_myanmar_ssc) {
			frm.set_value("custom_bcn_is_one_time_contribution", 0);
		}
	}
});