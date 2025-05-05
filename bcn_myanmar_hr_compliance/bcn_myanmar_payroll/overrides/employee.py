# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe.utils import getdate, month_diff, nowdate

# from erpnext.setup.doctype.employee.employee import Employee
from hrms.overrides.employee_master import EmployeeMaster

class BCNEmployee(EmployeeMaster):
	def validate(self):
		super(BCNEmployee, self).validate()

		""" Validate Enable SSC """
		if self.custom_bcn_enable_ssc:
			if not self.custom_bcn_ssc_hscis_category:
				frappe.throw("Please select `Health and Social Care Insurance System Category` for Employee")
		else:
			self.custom_bcn_ssc_hscis_category = None

		self.validate_employee_hscisc()

	def validate_employee_hscisc(self):
		age = (month_diff(getdate(nowdate()), getdate(self.date_of_birth))) /12

		if age <= 60:
			if self.custom_bcn_ssc_hscis_category != "60yrs old and under":
				frappe.throw(f"Employee {self.employee_name} must be selected `60yrs old and under`")
		else:
			if self.custom_bcn_ssc_hscis_category != "Over 60yrs old":
				frappe.throw(f"Employee {frappe.bold(self.employee_name)} must be selected `Over 60yrs old`")