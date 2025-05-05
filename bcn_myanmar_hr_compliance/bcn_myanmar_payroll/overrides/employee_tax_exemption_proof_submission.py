# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from hrms.payroll.doctype.employee_tax_exemption_proof_submission.employee_tax_exemption_proof_submission import (
    EmployeeTaxExemptionProofSubmission
)
from hrms.hr.utils import (
	validate_active_employee,	
	validate_tax_declaration,
)
from bcn_myanmar_hr_compliance.bcn_myanmar_payroll.utils import (
	validate_exemption_from_date,
    validate_duplicate_exemption_for_payroll_period,
	validate_existing_salary_slip_of_selected_exemption_from_date
)

class BCNEmployeeTaxExemptionProofSubmission(EmployeeTaxExemptionProofSubmission):
	def validate(self):
		validate_active_employee(self.employee)
		validate_tax_declaration(self.tax_exemption_proofs)	

		validate_exemption_from_date(self.custom_bcn_from_date, self.payroll_period)	
		validate_duplicate_exemption_for_payroll_period(
			self.doctype, self.name, self.payroll_period, self.custom_bcn_from_date, self.employee
		)
		validate_existing_salary_slip_of_selected_exemption_from_date(
			self.custom_bcn_from_date, self.employee
		)
		
		self.set_total_actual_amount()
		self.set_total_exemption_amount()
		self.calculate_hra_exemption()
