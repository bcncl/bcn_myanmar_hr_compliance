# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe.utils import flt, ceil
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.utils import sanitize_expression

class BCNSalarySlip(SalarySlip):	
	def compute_income_tax_breakup(self):
		if not self.payroll_period:
			return

		self.standard_tax_exemption_amount = 0
		self.tax_exemption_declaration = 0
		self.deductions_before_tax_calculation = 0

		self.non_taxable_earnings = self.compute_non_taxable_earnings()
		
		self.custom_bcn_total_contributions = self.compute_total_contributions()
		
		ctc_without_contributions = self.compute_ctc()

		self.ctc = ctc_without_contributions  + self.custom_bcn_total_contributions 

		self.income_from_other_sources = self.get_income_form_other_sources()

		self.total_earnings = ctc_without_contributions + self.income_from_other_sources

		if hasattr(self, "tax_slab"):
			self.custom_bcn_myanmar_pit_applied = self.tax_slab.custom_bcn_is_myanmar_pit_compliance

			if self.tax_slab.allow_tax_exemption:
				self.standard_tax_exemption_amount = self.tax_slab.standard_tax_exemption_amount
				self.deductions_before_tax_calculation = (
					self.compute_annual_deductions_before_tax_calculation()
				)

			self.tax_exemption_declaration = (
				self.get_total_exemption_amount() - self.standard_tax_exemption_amount
			)

		self.annual_taxable_amount = self.total_earnings - (
			self.non_taxable_earnings
			+ self.deductions_before_tax_calculation
			+ self.tax_exemption_declaration
			+ self.standard_tax_exemption_amount
		)

		self.income_tax_deducted_till_date = self.get_income_tax_deducted_till_date()

		if hasattr(self, "total_structured_tax_amount") and hasattr(self, "current_structured_tax_amount"):
			self.future_income_tax_deductions = (
				self.total_structured_tax_amount
				+ self.get("full_tax_on_additional_earnings", 0)
				- self.income_tax_deducted_till_date
			)

			self.current_month_income_tax = self.current_structured_tax_amount + self.get(
				"full_tax_on_additional_earnings", 0
			)

			# non included current_month_income_tax separately as its already considered
			# while calculating income_tax_deducted_till_date

			self.total_income_tax = self.income_tax_deducted_till_date + self.future_income_tax_deductions			

		# Myanmar PIT
		if self.custom_bcn_myanmar_pit_applied:
			if self.total_earnings > self.standard_tax_exemption_amount:				
				basic_relief = self.total_earnings * 0.2
				self.standard_tax_exemption_amount = basic_relief if basic_relief < 10000000 else 10000000		

			if self.annual_taxable_amount < 0.0:
				self.annual_taxable_amount = 0.0
	
	def get_total_exemption_amount(self):
		total_exemption_amount = 0
		if self.tax_slab.allow_tax_exemption:
			
			if self.deduct_tax_for_unsubmitted_tax_exemption_proof:
				exemption_proof = frappe.db.get_list(
					"Employee Tax Exemption Proof Submission",
					filters={
						"employee": self.employee, 
						"payroll_period": self.payroll_period.name, 						
						"custom_bcn_from_date": ["<=", self.posting_date],
						"docstatus": 1
					},
					pluck="exemption_amount",
					order_by="custom_bcn_from_date desc",
					limit=1
				)
				if exemption_proof:
					total_exemption_amount = exemption_proof[0]
			else:
				declaration = frappe.db.get_list(
					"Employee Tax Exemption Declaration",
					filters={
						"employee": self.employee, 
						"payroll_period": self.payroll_period.name,
						"custom_bcn_from_date": ["<=", self.posting_date], 
						"docstatus": 1
					},
					pluck="total_exemption_amount",
					order_by="custom_bcn_from_date desc",
					limit=1
				)
				if declaration:
					total_exemption_amount = declaration[0]
			

		if self.tax_slab.standard_tax_exemption_amount:			
			if self.custom_bcn_myanmar_pit_applied and self.total_earnings and self.standard_tax_exemption_amount:
				if self.total_earnings <= self.standard_tax_exemption_amount:
					total_exemption_amount += flt(self.standard_tax_exemption_amount)
				else:
					basic_relief = self.total_earnings * 0.2
					self.standard_tax_exemption_amount = basic_relief if basic_relief < 10000000 else 10000000
					total_exemption_amount += flt(self.standard_tax_exemption_amount)
			else:
				total_exemption_amount += flt(self.standard_tax_exemption_amount)	
		
		return total_exemption_amount
	
	@frappe.whitelist()
	def get_emp_and_working_day_details(self):
		if self.employee:
			self.set("custom_bcn_contributions", [])

		super(BCNSalarySlip, self).get_emp_and_working_day_details()	
	
	def set_salary_structure_doc(self) -> None:
		self._salary_structure_doc = frappe.get_cached_doc("Salary Structure", self.salary_structure)
		
		# sanitize condition and formula fields
		for table in ("earnings", "deductions", "custom_bcn_contributions"):			
			for row in self._salary_structure_doc.get(table):
				row.condition = sanitize_expression(row.condition)
				row.formula = sanitize_expression(row.formula)

	def set_precision_for_component_amounts(self):
		"""Calculate conribution components"""
		if self.salary_structure:
			self.calculate_component_amounts("custom_bcn_contributions")			
		
		"""Set Precision"""
		for component_type in ("earnings", "deductions", "custom_bcn_contributions"):
			for component_row in self.get(component_type):
				component_row.amount = flt(component_row.amount, component_row.precision("amount"))

	def set_net_pay(self):
		super(BCNSalarySlip, self).set_net_pay()

		self.custom_bcn_total_contribution = self.get_component_totals("custom_bcn_contributions")
		self.custom_bcn_base_total_contribution = flt(
			flt(self.custom_bcn_total_contribution) * flt(self.exchange_rate), self.precision("custom_bcn_base_total_contribution")
		)
	
	def calculate_component_amounts(self, component_type):
		if not getattr(self, "_salary_structure_doc", None):
			self.set_salary_structure_doc()

		self.add_structure_components(component_type)
		self.add_additional_salary_components(component_type)
		if component_type == "earnings":
			self.add_employee_benefits()
		elif component_type == "deductions":
			self.add_tax_components()
		else: 
			self.add_employer_contributions()
			
	def add_employer_contributions(self):
		self.previous_contributions = self.get_salary_slip_details(
			self.payroll_period.start_date, self.start_date, parentfield="custom_bcn_contributions"
		)
		
		self.current_month_structured_contribution = 0.0
		for contribution in  self.custom_bcn_contributions:
			self.current_month_structured_contribution += flt(contribution.amount, contribution.precision("amount"))

		self.future_structured_contributions = 0.0
		self.future_structured_contributions = (
			self.current_month_structured_contribution * (ceil(self.remaining_sub_periods) - 1)
		)

		self.custom_bcn_contributed_amount_till_date = self.previous_contributions + self.current_month_structured_contribution
		self.custom_bcn_current_month_contribution = self.current_month_structured_contribution
		self.custom_bcn_future_contribution = self.future_structured_contributions

		return self.previous_contributions, self.current_month_structured_contribution, self.future_structured_contributions

	def compute_total_contributions(self):
		if hasattr(self, "previous_contributions"):
			return (
				self.previous_contributions
				+ self.current_month_structured_contribution
				+ self.future_structured_contributions		
			)
		return 0.0

	
	