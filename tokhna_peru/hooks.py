# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tokhna_peru"
app_title = "Tokhna Peru"
app_publisher = "Tokhna"
app_description = "Peru localization for ERPNext"
app_icon = "octicon octicon-gear"
app_color = "grey"
app_email = "info@tokhna.dev"
app_license = "MIT"
fixtures = [
    {
        "dt": "Custom Field",
        "filters": 
            [
                ["dt", "in", ("Supplier", "Company", "Customer", "Sales Invoice", "Item", "Warehouse", "UOM", "Purchase Invoice", "Delivery Note")]
            ]
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tokhna_peru/css/tokhna_peru.css"
# app_include_js = "/assets/tokhna_peru/js/tokhna_peru.js"

# include js, css files in header of web template
# web_include_css = "/assets/tokhna_peru/css/tokhna_peru.css"
# web_include_js = "/assets/tokhna_peru/js/tokhna_peru.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Company": "public/js/company.js",
    "Customer": "public/js/customer.js",
    "Supplier": "public/js/supplier.js",
    "Delivery Note": "public/js/delivery_note.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "tokhna_peru.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tokhna_peru.install.before_install"
after_install = "tokhna_peru.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tokhna_peru.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"before_submit": "tokhna_peru.tokhna_peru.facturacion_electronica.validate_default_fields",
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"tokhna_peru.tasks.all"
# 	],
# 	"daily": [
# 		"tokhna_peru.tasks.daily"
# 	],
# 	"hourly": [
# 		"tokhna_peru.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tokhna_peru.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tokhna_peru.tasks.monthly"
# 	]
    "cron": {
        "30 0 * * *":[
            "tokhna_peru.tasks.daily"
        ],
        "30 12 * * *":[
            "tokhna_peru.tasks.daily"
        ],
    }
}

# Testing
# -------

# before_tests = "tokhna_peru.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tokhna_peru.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tokhna_peru.task.get_dashboard_data"
# }

