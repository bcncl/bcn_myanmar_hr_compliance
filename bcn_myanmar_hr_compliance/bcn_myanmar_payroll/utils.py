# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import (
    formatdate,
    get_first_day,
    get_last_day,
    get_link_to_form,
    getdate,
)
from hrms.hr.utils import DuplicateDeclarationError


def validate_exemption_from_date(from_date, payroll_period):
    start_date, end_date = frappe.get_cached_value(
        "Payroll Period", payroll_period, ["start_date", "end_date"]
    )
    if not (getdate(start_date) <= getdate(from_date) <= getdate(end_date)):
        frappe.throw(
            _(
                "The `From date` must be between the start date and end date of the payroll period."
            )
        )


def validate_duplicate_exemption_for_payroll_period(
    doctype, docname, payroll_period, from_date, employee
):
    start_date = getdate(get_first_day(from_date))
    end_date = getdate(get_last_day(from_date))
    from_date = getdate(from_date)

    existing_record = frappe.db.exists(
        doctype,
        {
            "payroll_period": payroll_period,
            "custom_bcn_from_date": ["between", (start_date, end_date)],
            "employee": employee,
            "docstatus": 1,
            "name": ["!=", docname],
        },
    )

    if existing_record:
        frappe.throw(
            _("{0} already exists for employee {1} and period {2} ({3})").format(
                doctype, employee, payroll_period, from_date.strftime("%B")
            ),
            DuplicateDeclarationError,
        )


def validate_existing_salary_slip_of_selected_exemption_from_date(from_date, employee):
    existing_salary_slip = frappe.db.exists(
        "Salary Slip",
        {
            "docstatus": 1,
            "employee": employee,
            "start_date": [">=", getdate(from_date)],
        },
    )

    if existing_salary_slip:
        frappe.throw(
            _(
                "Salary Slip aleardy submitted for Employee {0} on this period {1}"
            ).format(
                frappe.bold(get_link_to_form("Employee", employee)),
                frappe.bold(formatdate(from_date)),
            )
        )
