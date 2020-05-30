# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tokhna and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json

class Autenticacion(Document):
	pass

@frappe.whitelist()
def test_connection(url, token):
	headers = {
			"Authorization": "Bearer " + token,
			"Content-Type":  "application/json"
	}
	response = requests.post(url, headers=headers)
	return json.loads(response.content)

def get_autentication(company):
	try:
		authentication = frappe.get_doc("Autenticacion", company)
		token = authentication.get("token")
	except:
		headers = {}
	else:
		headers = {
			"Authorization": "Bearer " + token,
			"Content-Type": "application/json"
		}
	return headers

def get_url(company):
	try:
		authentication = frappe.get_doc("Autenticacion", company)
		url = authentication.get("ruta")
	except:
		url = ""
	return url