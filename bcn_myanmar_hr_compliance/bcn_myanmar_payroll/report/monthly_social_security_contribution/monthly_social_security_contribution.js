// Copyright (c) 2025, Business Centric Network Company Limited and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Social Security Contribution"] = {
	"filters": [
		// {
		// 	fieldname: "from_date",
		// 	label: __("From"),
		// 	fieldtype: "Date",
		// 	default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		// 	reqd: 1,
		// 	width: "100px",
		// },
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
			hidden: 1
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
			"on_change": function(rpt) {
				set_company_ssc_reg_no(rpt)
			}
		},

		{
			fieldname: "company_ssc_reg_no",
			label: __("Company SSC Registration No"),
			fieldtype: "Data",
			width: "100px",
			read_only: 1	
		},
	],
	onload(rpt) {
		set_company_ssc_reg_no(rpt)
	}
};

const set_company_ssc_reg_no = (rpt) => {
	rpt.set_filter_value("company_ssc_reg_no", null)
	let company =rpt.get_filter_value("company")
	
	if (!company) return

	frappe.db.get_value("Company", company, "custom_bcn_ssc_registration_no")
		.then(r => {
			rpt.set_filter_value("company_ssc_reg_no", r.message.custom_bcn_ssc_registration_no)
		})
}
