# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

from collections import defaultdict

import erpnext
import frappe
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from frappe import _, bold
from frappe.query_builder.functions import Coalesce, Count
from frappe.utils import flt, formatdate
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry


class BCNPayrollEntry(PayrollEntry):
	@frappe.whitelist()
	def submit_salary_slips(self):
		self.validate_contribution_expense_account()
		super().submit_salary_slips()

	def validate_contribution_expense_account(self):
		salary_slip_list_query = frappe.qb.get_query(
			"Salary Slip",
			filters={"docstatus": 0, "payroll_entry": self.name},
		)
		salary_slip_list = salary_slip_list_query.run(pluck=True)

		contribution_component_count_query = frappe.qb.get_query(
			"Salary Detail",
			fields=[{"COUNT": "name", "as": "component_count"}],
			filters={
				"parenttype": "Salary Slip",
				"parentfield": "custom_bcn_contributions",
				"parent": ["in", salary_slip_list],
			}
		)
		contribution_component_count = contribution_component_count_query.run(as_list=True)

		if (
			contribution_component_count[0][0] > 0
			and not self.custom_bcn_contribution_expense_account
		):
			frappe.throw(
				_("""Contribution expense account must be set on `Payroll Entry`
				for salary slip which includes `Contribution Component`.""")
			)

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

		precision = frappe.get_precision(
			"Journal Entry Account", "debit_in_account_currency"
		)

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
				employee_wise_accounting_enabled,
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
					precision,
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
				user_remark=_(
					"Accrual Journal Entry for salaries from {0} to {1}"
				).format(self.start_date, self.end_date),
				submit_journal_entry=True,
				submitted_salary_slips=submitted_salary_slips,
				employee_wise_accounting_enabled=employee_wise_accounting_enabled,
			)

			self.create_er_contribution_journal_entry()

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
					component_dict[key] = (
						component_dict.get(key, 0) + amount_against_cost_center
					)

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
		precision,
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

	def create_er_contribution_journal_entry(self):
		ss = frappe.qb.DocType("Salary Slip")
		sscd = frappe.qb.DocType("BCN Contribution Detail")
		salary_slips = (
			frappe.qb.from_(ss)
			.select(
				ss.name,
				ss.custom_bcn_total_contribution,
				sscd.salary_component,
				sscd.amount,
			)
			.join(sscd)
			.on(ss.name == sscd.parent)
			.where(
				(ss.docstatus == 1)
				& (ss.custom_bcn_myanmar_ssc_applied == 1)
				& (ss.start_date >= self.start_date)
				& (ss.end_date <= self.end_date)
				& (ss.payroll_entry == self.name)
			)
		).run(as_dict=True)

		payable_account_details = {}
		ssb_components = []
		unique_contribution_amount = {}

		# frappe.throw(f'HERE: {salary_slips}')
		if len(salary_slips) > 0:

			for slip in salary_slips:
				if slip.salary_component not in ssb_components:
					ssb_components.append(slip.salary_component)
				payable_account_details[(slip.name, slip.salary_component)] = slip

				unique_contribution_amount[slip["name"]] = slip[
					"custom_bcn_total_contribution"
				]

			component_details = frappe.db.get_all(
				"Salary Component Account",
				filters={"company": self.company, "parent": ["In", ssb_components]},
				fields=["parent", "account"],
			)

			component_details_map = {
				component.parent: component.account for component in component_details
			}

			for slip in salary_slips:
				payable_account_details_map = payable_account_details.get(
					(slip.name, slip.salary_component)
				)
				account = component_details_map.get(slip.salary_component)
				payable_account_details_map["account"] = account

			total_contribution_amount = sum(unique_contribution_amount.values())

			ssb_details = defaultdict(float)
			for entry in payable_account_details.values():
				ssb_details[entry["account"]] += entry["amount"]

			""" Get and Validate Contribution Expense Account """
			contribution_expense_account = self.custom_bcn_contribution_expense_account
			if not contribution_expense_account:
				contribution_expense_account = frappe.db.get_value(
					"Company",
					self.company,
					"custom_bcn_default_contribution_expense_account",
				)

			if not contribution_expense_account:
				frappe.throw(
					f"The Contribution Expense Account is required. Please configure it in either the {frappe.bold('Payroll Entry')} or the {frappe.bold('Company')}"
				)

			cost_center = self.cost_center or frappe.db.get_value(
				"Company", self.company, "cost_center"
			)
			company_currency = erpnext.get_company_currency(self.company)
			message = f"Contribution Expense Journal Entry for salaries from {bold(formatdate(self.start_date, 'dd/MM/yyyy'))} to {bold(formatdate(self.end_date, 'dd/MM/yyyy'))}"

			""" Create Contributon Journal Entry """
			je = frappe.new_doc("Journal Entry")
			je.posting_date = self.posting_date
			je.company = self.company
			je.voucher_type = "Journal Entry"
			je.user_remark = message
			je.remark = f"Note: {message}"

			if self.currency != company_currency:
				je.multi_currency = 1
				total_contribution_amount = (
					total_contribution_amount * self.exchange_rate
				)

			je.append(
				"accounts",
				{
					"account": contribution_expense_account,
					"cost_center": cost_center,
					"debit_in_account_currency": total_contribution_amount,
					"credit_in_account_currency": 0.0,
					"reference_type": "Payroll Entry",
					"reference_name": self.name,
				},
			)

			for ssb_account in dict(ssb_details).keys():
				ssb_amount = dict(ssb_details).get(ssb_account)

				if self.currency != company_currency:
					ssb_amount = ssb_amount * self.exchange_rate

				je.append(
					"accounts",
					{
						"account": ssb_account,
						"cost_center": cost_center,
						"debit_in_account_currency": 0.0,
						"credit_in_account_currency": ssb_amount,
						"reference_type": "Payroll Entry",
						"reference_name": self.name,
					},
				)

			je.save()
			je.submit()
