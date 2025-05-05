# Copyright (c) 2025, Business Centric Network Company Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import get_first_day

def execute(filters=None):
	columns = get_columns(filters)
	salaries = get_salary_slip(filters)
	salary_name_list = []
	employee_salary_map = {}
	employee_list = []

	for salary in salaries:
		salary_name_list.append(salary.name)
		employee_salary_map[salary.name]= salary
		employee_list.append(salary.employee)
	

	employees = get_employee(filters, employee_list)
	employee_map = {emp.name: emp for emp in employees}

	deductions = get_salary_deductions_detail(salary_name_list)

	contributions = get_contribution_detail(salary_name_list)

	# frappe.throw(f'foo {contributions}')

	total_employee_ssc = 0
	total_employer_ssc = 0

	for contribution in contributions:
		contribution_map = contributions.get(contribution)
		
		employee_salary = {
			"employer_ssc": 0,
			"employer_injury": 0
		}		

		if contribution_map:
			employee_salary = employee_salary_map.get(contribution_map.parent)

			if contribution_map.salary_component in ["SSC 2% (ER)", "SSC 2.5% (ER)"]:
				employee_salary.setdefault("employer_ssc", contribution_map.amount or 0)	
				
			if contribution_map.salary_component == "SSC 1% (ER)":
				employee_salary.setdefault("employer_injury", contribution_map.amount or 0)	
				
	
	for slip in salaries:
		employee_salary = employee_salary_map.get(slip.name)
		employee= employee_map.get(slip.employee)

		deduction = deductions.get(slip.name)

		employee_salary.setdefault("employee", employee.name)	
		employee_salary.setdefault("ssn_no", employee.custom_bcn_ssc_registration_no)
		employee_salary.setdefault("gender", employee.gender)
		employee_salary.setdefault("payment", 300000 if slip.gross_pay > 300000 else slip.gross_pay)
		
		if deduction:
			employee_salary.setdefault("employee_ssc", deduction.amount)
			

		total_employee_ssc = slip.employee_ssc or 0.0
		total_employer_ssc = slip.employer_ssc + slip.employer_injury or 0.0
		
		employee_salary.setdefault("total_employee_ssc", total_employee_ssc)
		employee_salary.setdefault("total_employer_ssc", total_employer_ssc)
		
		employee_salary.setdefault("total_ssc", total_employer_ssc + total_employee_ssc)
			
	
	data = salaries
	return columns, data

def get_columns(filters):
	columns = [
		{
            "label": _("Employee"),
            "fieldtype": "Link",
            "fieldname": "employee",
            "options": "Employee",
            "width": 250
        },
        

		{
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "fieldname": "employee_name",
            "width": 200,
			"hidden": 1
        },
        
        {
            "label": _("SSC Registration No"),
            "fieldtype": "Data",
            "fieldname": "ssn_no",
            "width": 100
        },
        
        {
            "label": _("Gender"),
            "fieldtype": "Link",
            "fieldname": "gender",
            "options": "Gender",
            "width": 100
        },
        
        {
            "label": _("Payment"),
            "fieldtype": "Currency",
            "fieldname": "payment",
            "width": 150
        },

		{
            "label": _("Employer SSC"),
            "fieldtype": "Currency",
            "fieldname": "employer_ssc",
            "width": 150
        },
        
		{
            "label": _("Employee SSC"),
            "fieldtype": "Currency",
            "fieldname": "employee_ssc",
            "width": 150
        },		

		{
            "label": _("Employer Injury"),
            "fieldtype": "Currency",
            "fieldname": "employer_injury",
            "width": 150
        },

		{
            "label": _("Total Employer SSC"),
            "fieldtype": "Currency",
            "fieldname": "total_employer_ssc",
            "width": 150
        },

		{
            "label": _("Total Employee SSC"),
            "fieldtype": "Currency",
            "fieldname": "total_employee_ssc",
            "width": 150
        },

		{
            "label": _("Total SSC"),
            "fieldtype": "Currency",
            "fieldname": "total_ssc",
            "width": 150
        },

		{
            "label": _("Remark"),
            "fieldtype": "Data",
            "fieldname": "remark",
            "width": 250
        },

	]

	return columns

def get_salary_slip(filters):
	upto_date = filters.upto_date
	from_date = get_first_day(upto_date)

	salary_filters = {
		"docstatus": 1,
		"company": filters.company,
		"posting_date": ["Between", [from_date, upto_date]]
	}

	if filters.employee:
		salary_filters.update({"employee": filters.employee})

	salaries = frappe.get_list("Salary Slip",
		filters=salary_filters,
		fields=[
			"name",
			"employee",
			"posting_date",
			"employee_name",
			"gross_pay",
		]
	)

	return salaries

def get_employee(filters, employee_list):
	return frappe.get_list("Employee",
		filters={
			"name": ["In", employee_list]
		},
		fields=[
			"name",
			"employee_name",
			"gender",			
			"custom_bcn_enable_ssc",
			"custom_bcn_ssc_registration_no"
		],
		order_by="name"
	)

def get_salary_deductions_detail(salary_name_list):	
	myanmar_compliance_component_list = frappe.get_list("Salary Component", 
		filters = {
			"custom_bcn_is_myanmar_ssc": 1,
			"type": "Deduction"
		}, 
		pluck = "name"
	)

	salary_detail = frappe.db.get_all("Salary Detail", 
		filters = {
			"parent": ["In", salary_name_list],
			"parentfield": "deductions",
			"salary_component": ["In", myanmar_compliance_component_list]
		},
		fields = [
			"parent",
			"salary_component",
			"amount"
		]
	)

	return {detail.parent: detail for detail in salary_detail}

def get_contribution_detail(salary_name_list):
	contribution_detail = frappe.db.get_all("BCN Contribution Detail", 
		filters = {
			"parent": ["In", salary_name_list]
		},
		fields = [
			"name",
			"parent",
			"salary_component",
			"amount"
		]
	)

	return {contribution.name: contribution for contribution in contribution_detail}
