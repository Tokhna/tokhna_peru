# -*- coding: utf-8 -*-
# Copyright (c) 2018, OVENUBE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TiposdeTransaccionSunat(Document):
	pass

@frappe.whitelist()
def get_tipo_transaccion(customer):
	cliente = frappe.get_doc("Customer", customer)
	if cliente.codigo_tipo_documento in ['-', '1', '4', '6']:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "VENTA INTERNA")
	elif cliente.codigo_tipo_documento == "0":
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "EXPORTACION")
	else:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "NO DOMICILIADO")
	return {"codigo": transaccion.codigo_tipo_transaccion, "descripcion": transaccion.name}

@frappe.whitelist()
def get_tipo_transaccion_compras(supplier):
	proveedor = frappe.get_doc("Supplier", supplier)
	if proveedor.codigo_tipo_documento in ['-', '1', '4', '6']:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "VENTA INTERNA")
	else:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "NO DOMICILIADO")
	return {"codigo": transaccion.codigo_tipo_transaccion, "descripcion": transaccion.name}

@frappe.whitelist()
def get_tipo_transaccion_fee(student):
	student = frappe.get_doc("Student", student)
	if student.codigo_tipo_documento in ['-', '1', '4', '6']:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "VENTA INTERNA")
	else:
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "NO DOMICILIADO")
	return {"codigo": transaccion.codigo_tipo_transaccion, "descripcion": transaccion.name}