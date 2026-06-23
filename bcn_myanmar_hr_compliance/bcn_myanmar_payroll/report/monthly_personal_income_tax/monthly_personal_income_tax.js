// Copyright (c) 2025, Business Centric Network Company Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Personal Income Tax"] = {
	filters: [
		{
			fieldname: "upto_date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "100px",
		},
		{
			fieldname: "currency",
			fieldtype: "Link",
			options: "Currency",
			label: __("Currency"),
			default: erpnext.get_currency(frappe.defaults.get_default("Company")),
			width: "50px",
			hidden: 1,
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			width: "100px",
		},

		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			width: "100px",
			reqd: 1,
		},
	],
};
