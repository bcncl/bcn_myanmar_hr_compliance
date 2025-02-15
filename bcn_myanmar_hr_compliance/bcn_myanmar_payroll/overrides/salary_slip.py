# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe.utils import flt
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

class BCNSalarySlip(SalarySlip):
	def compute_income_tax_breakup(self):
		super(BCNSalarySlip, self).compute_income_tax_breakup()
		if not hasattr(self, "tax_slab"):
			return

		if self.tax_slab.custom_bcn_is_myanmar_pit_compliance:
			if self.total_earnings > self.standard_tax_exemption_amount:
				self.tax_exemption_declaration +=  self.standard_tax_exemption_amount
				self.standard_tax_exemption_amount = 0.0

			if self.annual_taxable_amount < 0.0:
				self.annual_taxable_amount = 0.0

	def get_total_exemption_amount(self):
		total_exemption_amount = super(BCNSalarySlip, self).get_total_exemption_amount()
		if self.tax_slab.custom_bcn_is_myanmar_pit_compliance:
			if self.total_earnings > self.standard_tax_exemption_amount:
				total_exemption_amount -= flt(self.tax_slab.standard_tax_exemption_amount)
		
		return total_exemption_amount