import frappe

def execute():
	#frappe.db.truncate("BCN Contribution Detail")
	frappe.db.sql("""
		INSERT INTO `tabBCN Contribution Detail`
			(`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `salary_component`, `abbr`, `amount`, `year_to_date`, `additional_salary`, `is_recurring_additional_salary`, `statistical_component`, `depends_on_payment_days`, `exempted_from_income_tax`, `is_tax_applicable`, `is_flexible_benefit`, `variable_based_on_taxable_salary`, `do_not_include_in_total`, `deduct_full_tax_on_selected_payroll_date`, `condition`, `amount_based_on_formula`, `formula`, `default_amount`, `additional_amount`, `tax_on_flexible_benefit`, `tax_on_additional_salary`, `parent`, `parentfield`, `parenttype`)
		SELECT 
			`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `salary_component`, `abbr`, `amount`, `year_to_date`, `additional_salary`, `is_recurring_additional_salary`, `statistical_component`, `depends_on_payment_days`, `exempted_from_income_tax`, `is_tax_applicable`, `is_flexible_benefit`, `variable_based_on_taxable_salary`, `do_not_include_in_total`, `deduct_full_tax_on_selected_payroll_date`, `condition`, `amount_based_on_formula`, `formula`, `default_amount`, `additional_amount`, `tax_on_flexible_benefit`, `tax_on_additional_salary`, `parent`, `parentfield`, `parenttype`
		FROM 
			`tabSalary Detail`
		WHERE 
			`parentfield` = 'custom_bcn_contributions';
	""")
	frappe.db.delete("Salary Detail", filters={"parentfield": 'custom_bcn_contributions'})
	frappe.db.commit()