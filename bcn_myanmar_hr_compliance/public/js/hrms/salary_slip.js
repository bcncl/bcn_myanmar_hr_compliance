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
    }
});