# Copyright (c) 2025, Business Centric Network Company Limited and Contributors
# License: MIT. See license.txt


import re

import frappe
from frappe import _
from frappe.utils import cstr
from hrms.payroll.doctype.salary_structure.salary_structure import SalaryStructure
from hrms.payroll.utils import sanitize_expression


class BCNSalaryStructure(SalaryStructure):
    def sanitize_condition_and_formula_fields(self):
        for table in ("earnings", "deductions", "custom_bcn_contributions"):
            for row in self.get(table):
                row.condition = row.condition.strip() if row.condition else ""
                row.formula = row.formula.strip() if row.formula else ""
                row._condition, row.condition = row.condition, sanitize_expression(
                    row.condition
                )
                row._formula, row.formula = row.formula, sanitize_expression(
                    row.formula
                )

    def set_missing_values(self):
        overwritten_fields = [
            "depends_on_payment_days",
            "variable_based_on_taxable_salary",
            "is_tax_applicable",
            "is_flexible_benefit",
        ]
        overwritten_fields_if_missing = ["amount_based_on_formula", "formula", "amount"]
        for table in ["earnings", "deductions", "custom_bcn_contributions"]:
            for d in self.get(table):
                component_default_value = frappe.db.get_value(
                    "Salary Component",
                    cstr(d.salary_component),
                    overwritten_fields + overwritten_fields_if_missing,
                    as_dict=1,
                )
                if component_default_value:
                    for fieldname in overwritten_fields:
                        value = component_default_value.get(fieldname)
                        if d.get(fieldname) != value:
                            d.set(fieldname, value)

                    if not (d.get("amount") or d.get("formula")):
                        for fieldname in overwritten_fields_if_missing:
                            d.set(fieldname, component_default_value.get(fieldname))

    def validate_payment_days_based_dependent_component(self):
        abbreviations = self.get_component_abbreviations()
        for component_type in ("earnings", "deductions", "custom_bcn_contributions"):
            for row in self.get(component_type):
                if (
                    row.formula
                    and row.depends_on_payment_days
                    # check if the formula contains any of the payment days components
                    and any(
                        re.search(r"\b" + abbr + r"\b", row.formula)
                        for abbr in abbreviations
                    )
                ):
                    message = _(
                        "Row #{0}: The {1} Component has the options {2} and {3} enabled."
                    ).format(
                        row.idx,
                        frappe.bold(row.salary_component),
                        frappe.bold(_("Amount based on formula")),
                        frappe.bold(_("Depends On Payment Days")),
                    )
                    message += "<br><br>" + _(
                        "Disable {0} for the {1} component, to prevent the amount from being deducted twice, as its formula already uses a payment-days-based component."
                    ).format(
                        frappe.bold(_("Depends On Payment Days")),
                        frappe.bold(row.salary_component),
                    )
                    frappe.throw(message, title=_("Payment Days Dependency"))

    def validate_formula_setup(self):
        for table in ["earnings", "deductions", "custom_bcn_contributions"]:
            for row in self.get(table):
                if not row.amount_based_on_formula and row.formula:
                    frappe.msgprint(
                        _(
                            "{0} Row #{1}: Formula is set but {2} is disabled for the Salary Component {3}."
                        ).format(
                            table.capitalize(),
                            row.idx,
                            frappe.bold(_("Amount Based on Formula")),
                            frappe.bold(row.salary_component),
                        ),
                        title=_("Warning"),
                        indicator="orange",
                    )

    def reset_condition_and_formula_fields(self):
        # set old values (allowing multiline strings for better readability in the doctype form)
        for table in ("earnings", "deductions", "custom_bcn_contributions"):
            for row in self.get(table):
                row.condition = row._condition
                row.formula = row._formula

        self.db_update_all()
