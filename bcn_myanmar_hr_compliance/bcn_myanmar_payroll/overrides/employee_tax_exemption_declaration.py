# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

# import frappe
from hrms.payroll.doctype.employee_tax_exemption_declaration.employee_tax_exemption_declaration import (
	EmployeeTaxExemptionDeclaration
)
from hrms.hr.utils import (
	validate_active_employee,	
	validate_tax_declaration,
)
from bcn_myanmar_hr_compliance.bcn_myanmar_payroll.utils import (
	validate_duplicate_exemption_for_payroll_period
)

class BCNEmployeeTaxExemptionDeclaration(EmployeeTaxExemptionDeclaration):
	def validate(self):
		validate_active_employee(self.employee)
		validate_tax_declaration(self.declarations)
		validate_duplicate_exemption_for_payroll_period(
			self.doctype, self.name, self.payroll_period, self.custom_bcn_from_date, self.employee
		)
		self.set_total_declared_amount()
		self.set_total_exemption_amount()
		self.calculate_hra_exemption()
