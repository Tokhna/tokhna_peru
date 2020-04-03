# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import frappe
import os.path
import distutils.dir_util


def after_install():
    import_data()

def import_data():
    my_path = os.path.abspath(os.path.dirname(__file__))
    my_path = os.path.join(my_path, "imports/")

    try:
        path = os.path.join(my_path, "tipos_de_comprobante.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Comprobante')
                doc.codigo_tipo_comprobante = val[0]
                doc.nombre_tipo_comprobante = val[1]
                doc.descripcion_tipo_comprobante = val[2]
                doc.insert()
    except:
        print("Tipos de Comprobante ya migrado")

    try:
        path = os.path.join(my_path, "tipos_de_documento_de_identidad.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Documento de Identidad')
                doc.codigo_tipo_documento = val[0]
                doc.descripcion_tipo_documento = val[1]
                doc.insert()
    except:
        print("Tipos de Documento de Identidad ya migrado")

    try:
        path = os.path.join(my_path, "tipos_de_pago.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Pago')
                doc.codigo_tipo_pago = val[0]
                doc.descripcion_tipo_pago = val[1]
                doc.insert()
    except:
        print("Tipos de Pago ya migrado")

    try:
        path = os.path.join(my_path, "catalogo_de_existencias.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Catalogo de Existencias')
                doc.codigo_catalogo = val[0]
                doc.descripcion_catalogo = val[1]
                doc.insert()
    except:
        print("Catalogo de Existencias ya migrado")

    try:
        path = os.path.join(my_path, "tipos_de_existencia.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Existencia')
                doc.codigo_tipos_existencia = val[0]
                doc.descripcion_tipos_existencia = val[1]
                doc.insert()
    except:
        print("Tipos de Existencia ya migrado")

    try:
        path = os.path.join(my_path, "tipos_de_operaciones.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Operaciones')
                doc.codigo_tipos_operacion = val[0]
                doc.descripcion_tipos_operacion = val[1]
                doc.insert()
    except:
        print("Tipos de Operaciones ya migrado")

    try:
        path = os.path.join(my_path, "unidades_de_medida.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Unidades de Medida')
                doc.codigo_unidad_medida = val[0]
                doc.descripcion_unidad_medida = val[1]
                doc.insert()
    except:
        print("Unidades de Medida ya migrado")

    try:
        path = os.path.join(my_path, "tipos_de_transaccion.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Transaccion Sunat')
                doc.codigo_tipo_transaccion = val[0]
                doc.nombre_tipo_transaccion = val[1]
                doc.insert()
    except:
        print("Tipos de Transaccion Sunat ya migrado")

    try:
        path = os.path.join(my_path, "tipos_notas_credito.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Notas de Credito')
                doc.codigo_notas_credito = val[0]
                doc.nombre_notas_credito = val[1]
                doc.insert()
    except:
        print("Tipos de Notas de Credito ya migrado")

    try:
        path = os.path.join(my_path, "tipos_notas_debito.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Notas de Debito')
                doc.codigo_notas_debito = val[0]
                doc.nombre_notas_debito = val[1]
                doc.insert()
    except:
        print("Tipos de Notas de Debito ya migrado")

    try:
        path = os.path.join(my_path, "motivo_traslado.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Motivos de Traslado')
                doc.codigo_motivo_traslado = val[0]
                doc.nombre_motivo_traslado = val[1]
                doc.insert()
    except:
        print("Motivos de Traslado ya migrado")

    try:
        path = os.path.join(my_path, "tipos_transporte.csv")
        with open(path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            for idx, val in enumerate(reader):
                if idx == 0:
                    continue  # If csv have first row with headers

                # Do something with your data
                doc = frappe.new_doc('Tipos de Transporte')
                doc.codigo_tipo_transporte = val[0]
                doc.nombre_tipo_transporte = val[1]
                doc.insert()
    except:
        print("Tipos de Transporte ya migrado")
            