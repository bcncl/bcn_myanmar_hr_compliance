# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import flt, ceil
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.utils import sanitize_expression
from frappe.query_builder.functions import Count, Sum

class BCNSalarySlip(SalarySlip):
	def before_save(self):		
		self.check_draft_status_slip()
		
	def check_draft_status_slip(self):
		drafting_slip = frappe.db.get_list("Salary Slip", 
			filters = {	
				"docstatus": 0,
				"name": ["!=", self.name],
				"posting_date": ["<", self.posting_date],
				"employee": self.employee
			},
			or_filters = {
				"posting_date": ["between", [self.payroll_period.start_date, self.payroll_period.end_date]],
			},
			pluck = "name"
		)
		if len(drafting_slip) > 0:
			frappe.throw("Please submit the draft salary slip for last month first.")

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
				# if self.total_earnings > self.standard_tax_exemption_amount:
				# 	self.standard_tax_exemption_amount = self.tax_slab.standard_tax_exemption_amount
				# else:
				# 	self.standard_tax_exemption_amount = 0

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

			# ATTENTATION: reset minus value to 0
			if self.future_income_tax_deductions < 0:
				self.future_income_tax_deductions = 0

			if self.current_month_income_tax < 0:
				self.current_month_income_tax = 0

			# non included current_month_income_tax separately as its already considered
			# while calculating income_tax_deducted_till_date

			self.total_income_tax = self.income_tax_deducted_till_date + self.future_income_tax_deductions			

		# Myanmar PIT
		if self.custom_bcn_myanmar_pit_applied:
			if self.total_earnings > self.standard_tax_exemption_amount:				
				basic_relief = self.total_earnings * 0.2
				self.standard_tax_exemption_amount = basic_relief if basic_relief < 10000000 else 10000000	
			
			# ATTENTATION: reset minus value to 0
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
				if self.total_earnings > self.standard_tax_exemption_amount:
					basic_relief = self.total_earnings * 0.2
					self.standard_tax_exemption_amount = basic_relief if basic_relief < 10000000 else 10000000
				total_exemption_amount = flt(self.standard_tax_exemption_amount)				
			# else:
			# 	total_exemption_amount += flt(self.standard_tax_exemption_amount)	
		
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
		if component_type == "earnings":
			self.add_additional_salary_components(component_type)
			self.add_employee_benefits()
		elif component_type == "deductions":	
			self.add_additional_salary_components(component_type)		
			self.add_tax_components()
		else: 
			component_type = "custom_bcn_contributions"
			self.add_additional_salary_contribution_components(component_type)
			self.add_employer_contributions()
		
	def add_additional_salary_contribution_components(self, component_type):		
		additional_salaries = self.get_contribution_additional_salaries(
			self.employee, self.start_date, self.end_date, component_type
		)	
		
		for additional_salary in additional_salaries:
			self.update_component_row(
				self.get_salary_component_data(additional_salary.component),
				additional_salary.amount,
				component_type,
				additional_salary,
			)

	def get_salary_component_data(self, component):
		# get_cached_value doesn't work here due to alias "name as salary_component"
		return frappe.db.get_value(
			"Salary Component",
			component,
			(
				"name as salary_component",
				"depends_on_payment_days",
				"salary_component_abbr as abbr",
				"do_not_include_in_total",
				"is_tax_applicable",
				"is_flexible_benefit",
				"variable_based_on_taxable_salary",
			),
			as_dict=1,
			cache=True,
		)
	
	def get_contribution_additional_salaries(self, employee, start_date, end_date, component_type):		
		from frappe.query_builder import Criterion  
		
		if component_type == "custom_bcn_contributions":
			comp_type = "Contribution" 

			additional_sal = frappe.qb.DocType("Additional Salary")
			component_field = additional_sal.salary_component.as_("component")
			overwrite_field = additional_sal.overwrite_salary_structure_amount.as_("overwrite")

			additional_salary_list = (
				frappe.qb.from_(additional_sal)
				.select(
					additional_sal.name,
					component_field,
					additional_sal.type,
					additional_sal.amount,
					additional_sal.is_recurring,
					overwrite_field,
					additional_sal.deduct_full_tax_on_selected_payroll_date,
				)
				.where(
					(additional_sal.employee == employee)
					& (additional_sal.docstatus == 1)
					& (additional_sal.type == comp_type)
					& (additional_sal.disabled == 0)
				)
				.where(
					Criterion.any(
						[
							Criterion.all(
								[  # is recurring and additional salary dates fall within the payroll period
									additional_sal.is_recurring == 1,
									additional_sal.from_date <= end_date,
									additional_sal.to_date >= end_date,
								]
							),
							Criterion.all(
								[  # is not recurring and additional salary's payroll date falls within the payroll period
									additional_sal.is_recurring == 0,
									additional_sal.payroll_date[start_date:end_date],
								]
							),
						]
					)
				)
				.run(as_dict=True)
			)

			additional_salaries = []
			components_to_overwrite = []

			for d in additional_salary_list:
				if d.overwrite:
					if d.component in components_to_overwrite:
						frappe.throw(
						_(
						"Multiple Additional Salaries with overwrite property exist for Salary Component {0} between {1} and {2}."
						).format(frappe.bold(d.component), start_date, end_date),
						title=_("Error"),
						)

					components_to_overwrite.append(d.component)

				additional_salaries.append(d)

			return additional_salaries
		
	def add_employer_contributions(self):
		opening_contribution = self.get_opening_contributed_amount()

		self.previous_contributions = opening_contribution + self.get_contribution_details(
			self.payroll_period.start_date, self.start_date
		)		
		self.current_month_structured_contribution = 0.0
		self.one_time_contribution = 0.0
		for contribution in  self.custom_bcn_contributions:
			self.current_month_structured_contribution += flt(contribution.amount, contribution.precision("amount"))
			
			if contribution.is_one_time_contribution == 1:
				self.one_time_contribution += flt(contribution.amount, contribution.precision("amount"))
		
		self.future_structured_contributions = 0.0
		self.future_structured_contributions = (
			(self.current_month_structured_contribution - self.one_time_contribution) * (ceil(self.remaining_sub_periods) - 1)
		)
		
		self.custom_bcn_contributed_amount_till_date = self.previous_contributions + self.current_month_structured_contribution
		self.custom_bcn_current_month_contribution = self.current_month_structured_contribution
		self.custom_bcn_future_contribution = self.future_structured_contributions

		return self.previous_contributions, self.current_month_structured_contribution, self.future_structured_contributions
	
	def get_opening_contributed_amount(self):
		return self.get_opening_for("custom_bcn_contributed_amount_till_date", self.payroll_period.start_date, self.end_date) or 0

	def get_contribution_details(
		self,
		start_date,
		end_date,
		salary_component=None,
		field_to_select="amount",
	):
		ss = frappe.qb.DocType("Salary Slip")
		sd = frappe.qb.DocType("BCN Contribution Detail")

		if field_to_select == "amount":
			field = sd.amount
		else:
			field = sd.additional_amount

		query = (
			frappe.qb.from_(ss)
			.join(sd)
			.on(sd.parent == ss.name)
			.select(Sum(field))
			.where(ss.docstatus == 1)
			.where(ss.employee == self.employee)
			.where(ss.start_date.between(start_date, end_date))
			.where(ss.end_date.between(start_date, end_date))
		)
		
		if salary_component:
			query = query.where(sd.salary_component == salary_component)

		result = query.run()

		return flt(result[0][0]) if result else 0.0

	def compute_total_contributions(self):		
		if hasattr(self, "previous_contributions"):
			return (
				self.previous_contributions
				+ self.current_month_structured_contribution
				+ self.future_structured_contributions	
			)
		return 0.0

	def compute_annual_deductions_before_tax_calculation(self):
		annual_deductions_before_tax_calculation = super(BCNSalarySlip, self).compute_annual_deductions_before_tax_calculation()	

		return (
			self.get_opening_exempted_before_tax_calculation()
			+ annual_deductions_before_tax_calculation
		)
	
	def get_taxable_earnings_for_prev_period(self, start_date, end_date, allow_tax_exemption=False):
		taxable_earnings, exempted_amount = super(BCNSalarySlip, self).get_taxable_earnings_for_prev_period(start_date, end_date, allow_tax_exemption)

		opening_exempted_amount = self.get_opening_exempted_before_tax_calculation()
		if opening_exempted_amount:
			taxable_earnings -= opening_exempted_amount
			exempted_amount += opening_exempted_amount

		return taxable_earnings, exempted_amount
	
	def get_opening_exempted_before_tax_calculation(self):
		if self.payroll_period:
			return self.get_opening_for("custom_bcn_exempted_from_income_tax_till_date", self.payroll_period.start_date, self.end_date) or 0
		return 0
	
	def get_opening_for(self, field_to_select, start_date, end_date):
		if not (start_date and end_date):
			return

		if not hasattr(self, "_opening_salary_structure_assignment"):
			opening_salary_structure_assignment = frappe.db.get_list(
				"Salary Structure Assignment",
				filters={
					"employee": self.employee,
					"from_date": ("BETWEEN", (start_date, end_date)),
					"docstatus": 1,
				},
				fields=["*"],
				order_by="from_date",
				limit=1,
				# as_dict=True,
			)
			self._opening_salary_structure_assignment = opening_salary_structure_assignment and opening_salary_structure_assignment[0] or frappe._dict()

			# frappe.throw(f'Here: {self._opening_salary_structure_assignment}')
			# frappe.throw('foo')
		return self._opening_salary_structure_assignment.get(field_to_select) or 0
	
