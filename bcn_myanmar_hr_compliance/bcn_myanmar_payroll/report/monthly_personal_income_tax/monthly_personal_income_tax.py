# Copyright (c) 2025, Business Centric Network Company Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_first_day


def execute(filters=None):
    columns, data = [], []

    salaries = get_salaries(filters)
    salary_name_list = []
    employee_salary_map = {}
    employee_list = []

    for salary in salaries:
        salary_name_list.append(salary.name)
        employee_salary_map[salary.name] = salary
        employee_list.append(salary.employee)

    employee_info = get_employee(employee_list)
    employee_info_map = {emp.name: emp for emp in employee_info}

    salary_detail = get_salary_deductions_detail(salary_name_list)

    for salary in salaries:
        salary_dict = employee_salary_map.get(salary.name)

        employee_info_dict = employee_info_map.get(salary.employee)

        salary_detail_dict = salary_detail.get(salary.name)

        salary_dict.setdefault("employee", employee_info_dict.name)
        salary_dict.setdefault("designation", employee_info_dict.designation)
        salary_dict.setdefault("personal_income_tax", round(salary_detail_dict.amount))

    # frappe.throw(f'{employee_salary_map}')
    columns = get_columns(filters)
    data = salaries

    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Employee"),
            "fieldtype": "Link",
            "fieldname": "employee",
            "options": "Employee",
            "width": 250,
        },
        {
            "label": _("Designation"),
            "fieldtype": "Link",
            "fieldname": "designation",
            "options": "Designation",
            "width": 100,
        },
        {
            "label": _("Payment"),
            "fieldtype": "Currency",
            "fieldname": "gross_pay",
            "width": 150,
        },
        {
            "label": _("Personal Income Tax"),
            "fieldtype": "Currency",
            "fieldname": "personal_income_tax",
            "width": 150,
        },
        {
            "label": _("Remark"),
            "fieldtype": "Data",
            "fieldname": "remark",
            "width": 150,
        },
    ]

    return columns


def get_salaries(filters):
    upto_date = filters.upto_date
    from_date = get_first_day(upto_date)

    salary_filters = {
        "docstatus": 1,
        "company": filters.company,
        "posting_date": ["Between", [from_date, upto_date]],
    }

    if filters.employee:
        salary_filters.update({"employee": filters.employee})

    salaries = frappe.get_list(
        "Salary Slip",
        filters=salary_filters,
        fields=[
            "name",
            "employee",
            "employee_name",
            "gross_pay",
        ],
        order_by="employee",
    )

    return salaries


def get_employee(employee_list):
    return frappe.get_list(
        "Employee",
        filters={"name": ["In", employee_list]},
        fields=[
            "name",
            "employee_name",
            "designation",
            "custom_bcn_enable_ssc",
            "custom_bcn_ssc_registration_no",
        ],
        order_by="name",
    )


def get_salary_deductions_detail(salary_name_list):
    pit_component_list = frappe.get_list(
        "Salary Component", filters={"is_income_tax_component": 1}, pluck="name"
    )

    salary_detail = frappe.db.get_all(
        "Salary Detail",
        filters={
            "parent": ["In", salary_name_list],
            "parentfield": "deductions",
            "salary_component": ["In", pit_component_list],
        },
        fields=["parent", "salary_component", "amount"],
    )

    return {detail.parent: detail for detail in salary_detail}
