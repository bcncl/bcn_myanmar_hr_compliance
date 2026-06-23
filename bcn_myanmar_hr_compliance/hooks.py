app_name = "bcn_myanmar_hr_compliance"
app_title = "Myanmar HR Compliance"
app_publisher = "Business Centric Network Company Limited"
app_description = "HR Compliance for Myanmar"
app_email = "info@bcncl.com"
app_license = "agpl-3.0"

# Apps
# ------------------

required_apps = ["frappe/erpnext", "frappe/hrms"]
# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "bcn_myanmar_hr_compliance",
# 		"logo": "/assets/bcn_myanmar_hr_compliance/logo.png",
# 		"title": "BCN Myanmar HR Compliance",
# 		"route": "/bcn_myanmar_hr_compliance",
# 		"has_permission": "bcn_myanmar_hr_compliance.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bcn_myanmar_hr_compliance/css/bcn_myanmar_hr_compliance.css"
# app_include_js = "/assets/bcn_myanmar_hr_compliance/js/bcn_myanmar_hr_compliance.js"

# include js, css files in header of web template
# web_include_css = "/assets/bcn_myanmar_hr_compliance/css/bcn_myanmar_hr_compliance.css"
# web_include_js = "/assets/bcn_myanmar_hr_compliance/js/bcn_myanmar_hr_compliance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "bcn_myanmar_hr_compliance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Salary Component" : "public/js/hrms/salary_component.js",
	"Salary Structure" : "public/js/hrms/salary_structure.js",
	"Salary Slip": "public/js/hrms/salary_slip.js",
	"Payroll Entry": "public/js/hrms/payroll_entry.js",
    "Employee": "public/js/hrms/employee.js"
}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "bcn_myanmar_hr_compliance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "bcn_myanmar_hr_compliance.utils.jinja_methods",
# 	"filters": "bcn_myanmar_hr_compliance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "bcn_myanmar_hr_compliance.install.before_install"
after_install = "bcn_myanmar_hr_compliance.install.after_install"

# Uninstallation
# ------------

before_uninstall = "bcn_myanmar_hr_compliance.uninstall.before_uninstall"
# after_uninstall = "bcn_myanmar_hr_compliance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "bcn_myanmar_hr_compliance.utils.before_app_install"
# after_app_install = "bcn_myanmar_hr_compliance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "bcn_myanmar_hr_compliance.utils.before_app_uninstall"
# after_app_uninstall = "bcn_myanmar_hr_compliance.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "my_app.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bcn_myanmar_hr_compliance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Employee": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.employee.BCNEmployee",
    "Salary Structure": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.salary_structure.BCNSalaryStructure",
	"Salary Slip": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.salary_slip.BCNSalarySlip",
	"Employee Tax Exemption Declaration": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.employee_tax_exemption_declaration.BCNEmployeeTaxExemptionDeclaration",
	"Employee Tax Exemption Proof Submission": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.employee_tax_exemption_proof_submission.BCNEmployeeTaxExemptionProofSubmission",
	"Salary Component": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.salary_component.BCNSalaryComponent",
	"Payroll Entry": "bcn_myanmar_hr_compliance.bcn_myanmar_payroll.overrides.payroll_entry.BCNPayrollEntry"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bcn_myanmar_hr_compliance.tasks.all"
# 	],
# 	"daily": [
# 		"bcn_myanmar_hr_compliance.bcn_myanmar_payroll.utils.auto_create_payroll_period",
# 	],
# 	"hourly": [
# 		"bcn_myanmar_hr_compliance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bcn_myanmar_hr_compliance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bcn_myanmar_hr_compliance.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "bcn_myanmar_hr_compliance.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "my_app.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bcn_myanmar_hr_compliance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bcn_myanmar_hr_compliance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["bcn_myanmar_hr_compliance.utils.before_request"]
# after_request = ["bcn_myanmar_hr_compliance.utils.after_request"]

# Job Events
# ----------
# before_job = ["bcn_myanmar_hr_compliance.utils.before_job"]
# after_job = ["bcn_myanmar_hr_compliance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"bcn_myanmar_hr_compliance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
