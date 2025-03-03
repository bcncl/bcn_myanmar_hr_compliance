# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe

# from erpnext.setup.doctype.employee.employee import Employee
from hrms.overrides.employee_master import EmployeeMaster

class BCNEmployee(EmployeeMaster):
	def validate(self):
		super(BCNEmployee, self).validate()

		""" Validate Enable SSC """
		if self.custom_bcn_enable_ssc and not self.custom_bcn_ssc_hscis_category:
			frappe.throw("Please select `Health and Social Care Insurance System Category` for Employee")
		
	
	
			
		
	