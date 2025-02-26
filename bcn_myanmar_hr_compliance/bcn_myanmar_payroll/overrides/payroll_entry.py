# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from frappe.utils import (
	flt
)

import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)

class BCNPayrollEntry(PayrollEntry):
	@frappe.whitelist()
	def submit_salary_slips(self):
		self.validate_contirbution_expense_account()
		super(BCNPayrollEntry, self).submit_salary_slips()
	
	def validate_contirbution_expense_account(self):	
		salary_slip_list = frappe.get_list("Salary Slip",
			filters={
				"docstatus": 0,
				"payroll_entry": self.name
			},
			pluck = "name"
		)	

		contribution_component_count = frappe.get_all("Salary Detail", 
			filters = {
				"parenttype": "Salary Slip",
				"parentfield": "custom_bcn_contributions",
				"parent": ["in", salary_slip_list]
			},
			fields = "COUNT(name) component_count",
			as_list = True
		)

		if contribution_component_count[0][0] > 0 and not self.custom_bcn_contribution_expense_account:
			frappe.throw(f"""Contribution expense account must be set on `Payroll Entry` 
				for salary slip which includes `Contribution Component`.""")

	def make_accrual_jv_entry(self, submitted_salary_slips):			
		self.check_permission("write")
		employee_wise_accounting_enabled = frappe.db.get_single_value(
			"Payroll Settings", "process_payroll_accounting_entry_based_on_employee"
		)
		self.employee_based_payroll_payable_entries = {}
		self._advance_deduction_entries = []

		earnings = (
			self.get_salary_component_total(
				component_type="earnings",
				employee_wise_accounting_enabled=employee_wise_accounting_enabled,
			)
			or {}
		)

		deductions = (
			self.get_salary_component_total(
				component_type="deductions",
				employee_wise_accounting_enabled=employee_wise_accounting_enabled,
			)
			or {}
		)
		
		contributions = (
			self.get_contribution_component_total(
				component_type="custom_bcn_contributions",
				employee_wise_accounting_enabled=employee_wise_accounting_enabled,
			)
			or {}
		)		

		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		if earnings or deductions:
			accounts = []
			currencies = []
			payable_amount = 0
			accounting_dimensions = get_accounting_dimensions() or []
			company_currency = erpnext.get_company_currency(self.company)
	

			payable_amount = self.get_payable_amount_for_earnings_and_deductions(
				accounts,
				earnings,
				deductions,
				currencies,
				company_currency,
				accounting_dimensions,
				precision,
				payable_amount,
			)					

			payable_amount = self.set_accounting_entries_for_advance_deductions(
				accounts,
				currencies,
				company_currency,
				accounting_dimensions,
				precision,
				payable_amount,
			)

			# Contributions
			if self.custom_bcn_contribution_expense_account:
				contribution_amount = self.get_contribution_amount_for_contributions(
					accounts,
					contributions,
					currencies,
					company_currency,
					accounting_dimensions,
					precision
				)
				self.set_contribution_amount_against_contribution_expense_account(
					accounts,
					currencies,
					company_currency,
					accounting_dimensions,
					precision,
					contribution_amount,
					self.custom_bcn_contribution_expense_account,
				)	

			self.set_payable_amount_against_payroll_payable_account(
				accounts,
				currencies,
				company_currency,
				accounting_dimensions,
				precision,
				payable_amount,
				self.payroll_payable_account,
				employee_wise_accounting_enabled,
			)

			self.make_journal_entry(
				accounts,
				currencies,
				self.payroll_payable_account,
				voucher_type="Journal Entry",
				user_remark=_("Accrual Journal Entry for salaries from {0} to {1}").format(
					self.start_date, self.end_date
				),
				submit_journal_entry=True,
				submitted_salary_slips=submitted_salary_slips,
			)

	def get_contribution_component_total(
		self,
		component_type=None,
		employee_wise_accounting_enabled=False,
	):
		salary_components = self.get_salary_components(component_type)
		if salary_components:
			component_dict = {}

			for item in salary_components:
				if not self.should_add_component_to_accrual_jv(component_type, item):
					continue

				employee_cost_centers = self.get_payroll_cost_centers_for_employee(
					item.employee, item.salary_structure
				)
				
				for cost_center, percentage in employee_cost_centers.items():
					amount_against_cost_center = flt(item.amount) * percentage / 100
					
					key = (item.salary_component, cost_center)
					component_dict[key] = component_dict.get(key, 0) + amount_against_cost_center

					if employee_wise_accounting_enabled:
						self.set_employee_based_payroll_payable_entries(
							component_type, item.employee, amount_against_cost_center
						)
			
			account_details = self.get_account(component_dict=component_dict)			
			return account_details

	def set_contribution_amount_against_contribution_expense_account(
		self,
		accounts,
		currencies,
		company_currency,
		accounting_dimensions,
		precision,
		contribution_amount,
		contribution_expense_account,
	):
		# Contribution amount		
		contribution_amount = self.get_accounting_entries_and_payable_amount(
			contribution_expense_account,
			self.cost_center,
			contribution_amount,
			currencies,
			company_currency,
			0,
			accounting_dimensions,
			precision,
			entry_type="debit",
			accounts=accounts,
		)
		
	def get_contribution_amount_for_contributions(
		self,
		accounts,
		contributions,
		currencies,
		company_currency,
		accounting_dimensions,
		precision
	):		
		contribution_amount = 0.0
		
		for acc_cc, amount in contributions.items():
			contribution_amount = self.get_accounting_entries_and_payable_amount(
				acc_cc[0],
				acc_cc[1] or self.cost_center,
				amount,
				currencies,
				company_currency,
				contribution_amount,
				accounting_dimensions,
				precision,
				entry_type="credit",
				accounts=accounts,
			)	
		return contribution_amount * -1
