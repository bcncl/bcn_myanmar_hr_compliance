# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

from hrms.payroll.doctype.salary_component.salary_component import SalaryComponent

class BCNSalaryComponent(SalaryComponent):
	def validate(self):
		super(BCNSalaryComponent, self).validate()
		self.reset_component_properties()
	
	def reset_component_properties(self):
		if self.type in ["Contribution", "Earning"]:
			self.variable_based_on_taxable_salary = 0
			self.is_income_tax_component = 0
			self.exempted_from_income_tax = 0
			
		if self.type in ["Contribution", "Deduction"]:
			self.is_tax_applicable = 0
			self.deduct_full_tax_on_selected_payroll_date = 0

		