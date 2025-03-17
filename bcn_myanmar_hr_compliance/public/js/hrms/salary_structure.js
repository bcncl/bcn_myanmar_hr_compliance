// Copyright (c) 2025, Business Centric Network Company Limited and Contributors
// License: MIT. See license.txt

frappe.ui.form.on("Salary Structure", {
	onload: function(frm) {
		frm.events.set_query_contributions_component(frm);
	},
	refresh: function (frm) {
		frm.events.set_query_contributions_component(frm);
	},
	
	company: function (frm) {
		frm.events.set_query_contributions_component(frm);
	},

	set_query_contributions_component: function (frm) {
		if (!frm.doc.company) return;		
		frm.set_query("salary_component", "custom_bcn_contributions", function () {
			return {
				filters: { component_type: "contribution", company: frm.doc.company },
				query: "hrms.payroll.doctype.salary_structure.salary_structure.get_salary_component",
			};
		});
	},

	calculate_totals: function (frm) {		
		var tblcontri = frm.doc.custom_bcn_contributions || [];
		
		var total_contributions = 0;
		for (var i = 0; i < tblcontri.length; i++) {
			total_contributions += flt(tblcontri[i].amount);
		}
		
		frm.doc.custom_bcn_total_contribution = total_contributions;
		frm.refresh_field("custom_bcn_total_contribution")
	}
});

frappe.ui.form.on("BCN Contribution Detail", {
	form_render: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		hrms.payroll_utils.set_autocompletions_for_condition_and_formula(frm, row);
	},

	amount: function (frm) {
		frm.events.calculate_totals(frm);
	},

	custom_bcn_contribution_remove: function (frm) {
		frm.events.calculate_totals(frm);
	},

	formula: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.formula && !row?.amount_based_on_formula && !frm.alerted_rows.includes(cdn)) {
			frappe.msgprint({
				message: __(
					"{0} Row #{1}: {2} needs to be enabled for the formula to be considered.",
					[toTitle(row.parentfield), row.idx, __("Amount based on formula").bold()],
				),
				title: __("Warning"),
				indicator: "orange",
			});
			frm.alerted_rows.push(cdn);
		}
	},

	salary_component: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.salary_component) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Salary Component",
					name: child.salary_component,
				},
				callback: function (data) {
					if (data.message) {
						var result = data.message;
						frappe.model.set_value(cdt, cdn, "condition", result.condition);
						frappe.model.set_value(
							cdt,
							cdn,
							"amount_based_on_formula",
							result.amount_based_on_formula,
						);
						if (result.amount_based_on_formula == 1) {
							frappe.model.set_value(cdt, cdn, "formula", result.formula);
						} else {
							frappe.model.set_value(cdt, cdn, "amount", result.amount);
						}
						frappe.model.set_value(
							cdt,
							cdn,
							"statistical_component",
							result.statistical_component,
						);
						frappe.model.set_value(
							cdt,
							cdn,
							"depends_on_payment_days",
							result.depends_on_payment_days,
						);
						frappe.model.set_value(
							cdt,
							cdn,
							"do_not_include_in_total",
							result.do_not_include_in_total,
						);
						frappe.model.set_value(
							cdt,
							cdn,
							"variable_based_on_taxable_salary",
							result.variable_based_on_taxable_salary,
						);
						frappe.model.set_value(
							cdt,
							cdn,
							"is_tax_applicable",
							result.is_tax_applicable,
						);
						frappe.model.set_value(
							cdt,
							cdn,
							"is_flexible_benefit",
							result.is_flexible_benefit,
						);						
						frappe.model.set_value(
							cdt,
							cdn,
							"is_one_time_contribution",
							result.custom_bcn_is_one_time_contribution,
						);						
						refresh_field("custom_bcn_contributions");
					}
				},
			});
		}
	},

	amount_based_on_formula: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.amount_based_on_formula == 1) {
			frappe.model.set_value(cdt, cdn, "amount", null);
			const index = frm.alerted_rows.indexOf(cdn);
			if (index > -1) frm.alerted_rows.splice(index, 1);
		} else {
			frappe.model.set_value(cdt, cdn, "formula", null);
		}
	},
});