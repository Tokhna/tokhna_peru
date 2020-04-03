# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tokhna and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.setup.doctype.naming_series.naming_series import NamingSeries

class Configuracion(NamingSeries):
    def get_series(self):
        serie_ventas = self.get_options("Sales Invoice").replace("\n\n", "\n").split("\n")
        serie_guias = self.get_options("Delivery Note").replace("\n\n", "\n").split("\n")
        series_dict = {}
        series_dict["venta"] = []
        series_dict["guia"] = []
        for serie in serie_ventas:
            series_dict["venta"].append(serie)
        for serie in serie_guias:
            series_dict["guia"].append(serie)
        return series_dict

@frappe.whitelist()
def get_product_anticipo(company):
    configuracion = frappe.get_doc("Configuracion", company)
    return configuracion.anticipo

@frappe.whitelist()
def get_doc_serie(company, doctype, is_return="", contingencia="", codigo_tipo_documento="", codigo_comprobante="", es_nota_debito=""):
	doc_series = []
	series = frappe.get_doc("Configuracion", company).configuracion_series
	if doctype == "Sales Invoice":
		if is_return == "1":
			comprobante = frappe.get_doc("Tipos de Comprobante", "Nota de Crédito")
			if contingencia == "1":
				for serie in series:
					if codigo_tipo_documento == "6" or codigo_tipo_documento == "0":
						if serie.contingencia == "1" and serie.tipo_documento == "Nota de Crédito" and serie.tipo_comprobante == "Factura":
							doc_series.append(serie.serie_documento)
					else:
						if serie.contingencia == "1" and serie.tipo_documento == "Nota de Crédito" and serie.tipo_comprobante == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
			else:
				for serie in series:
					if codigo_tipo_documento == "6" or codigo_tipo_documento == "0":
						if serie.contingencia == "0" and serie.tipo_documento == "Nota de Crédito" and serie.tipo_comprobante == "Factura":
							doc_series.append(serie.serie_documento)
					else:
						if serie.contingencia == "0" and serie.tipo_documento == "Nota de Crédito" and serie.tipo_comprobante == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
		elif es_nota_debito == "1":
			comprobante = frappe.get_doc("Tipos de Comprobante", "Nota de Débito")
			if contingencia == "1":
				for serie in series:
					if codigo_tipo_documento == "6" or codigo_tipo_documento == "0":
						if serie.contingencia == "1" and serie.tipo_documento == "Nota de Débito" and serie.tipo_comprobante == "Factura":
							doc_series.append(serie.serie_documento)
					else:
						if serie.contingencia == "1" and serie.tipo_documento == "Nota de Débito" and serie.tipo_comprobante == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
			else:
				for serie in series:
					if codigo_tipo_documento == "6" or codigo_tipo_documento == "0":
						if serie.contingencia == "0" and serie.tipo_documento == "Nota de Débito" and serie.tipo_comprobante == "Factura":
							doc_series.append(serie.serie_documento)
					else:
						if serie.contingencia == "0" and serie.tipo_documento == "Nota de Débito" and serie.tipo_comprobante == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
		else:
			if codigo_tipo_documento == "6" or codigo_tipo_documento == "0":
				comprobante = frappe.get_doc("Tipos de Comprobante", "Factura")
				if contingencia == "1":
					for serie in series:
						if serie.contingencia == "1" and serie.tipo_documento == "Factura":
							doc_series.append(serie.serie_documento)
				else:
					for serie in series:
						if serie.contingencia == "0" and serie.tipo_documento == "Factura":
							doc_series.append(serie.serie_documento)
			else:
				comprobante = frappe.get_doc("Tipos de Comprobante", "Boleta de Venta")
				if contingencia == "1":
					for serie in series:
						if serie.contingencia == "1" and serie.tipo_documento == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
				else:
					for serie in series:
						if serie.contingencia == "0" and serie.tipo_documento == "Boleta de Venta":
							doc_series.append(serie.serie_documento)
	elif doctype == "Delivery Note":
		comprobante = frappe.get_doc("Tipos de Comprobante", "Guía de remisión - Remitente")
		if contingencia == "1":
			for serie in series:
				if serie.contingencia == "1" and serie.tipo_documento == "Guía de Remisión":
					doc_series.append(serie.serie_documento)
		else:
			for serie in series:
				if serie.contingencia == "0" and serie.tipo_documento == "Guía de Remisión":
					doc_series.append(serie.serie_documento)
	return {"codigo": comprobante.codigo_tipo_comprobante, "descripcion": comprobante.name, "series": doc_series}