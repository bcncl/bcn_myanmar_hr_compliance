// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Employee", {
	refresh(frm) {},
	custom_bcn_enable_ssc(frm) {
		if (frm.doc.custom_bcn_enable_ssc === 0) {
			frm.set_value("custom_bcn_ssc_registration_no", null);
			frm.set_value("custom_bcn_ssc_hscis_category", null);
		}
	},
});
