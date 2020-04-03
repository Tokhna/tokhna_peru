# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Facturación Electrónica"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Autenticacion",
					"onboard": 1,
                },
				{
                    "type": "doctype",
                    "name": "Configuracion",
					"onboard": 1,
                }
            ]
        },
        {
            "label": _("Libros Electronicós"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Libro Electronico de Ventas",
                },
                {
                    "type": "doctype",
                    "name": "Libro Electronico de Compras",
                },
                {
                    "type": "doctype",
                    "name": "Libro Electronico Diario",
                },
                {
                    "type": "doctype",
                    "name": "Libro Electronico de Inventario Permanente Valorizado",
                },
                {
                    "type": "doctype",
                    "name": "Libro Electronico Mayor",
                },
            ]
        },
        {
            "label": _("Configuración"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Motivos de Traslado",
                },
				{
                    "type": "doctype",
                    "name": "Tipos de Notas de Credito",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Notas de Debito",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Transaccion Sunat",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Transporte",
                },
                {
                    "type": "doctype",
                    "name": "Catalogo de Existencias",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Comprobante",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Documento de Identidad",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Existencia",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Operaciones",
                },
                {
                    "type": "doctype",
                    "name": "Tipos de Pago",
                },
                {
                    "type": "doctype",
                    "name": "Unidades de Medida",
                }
            ]
        }
    ]