# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from tokhna_peru.tokhna_peru.doctype.autenticacion.autenticacion import get_autentication, get_url
from tokhna_peru.tokhna_peru.utils import tipo_de_comprobante, get_serie_correlativo, get_moneda, get_igv, get_tipo_producto, get_serie_online, get_doc_conductor, get_doc_transportista, get_address_information
import requests
import json
import datetime

@frappe.whitelist()
def send_document(company, invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            return_type = return_serie = return_correlativo = codigo_nota_credito = party_name = ""
            address = {}
            try:
                if doctype == "Sales Invoice":
                    mult  = 1
                    monto_anticipo_neto = igv_anticipo = anticipo_amount = anticipo_total = 0
                    doc = frappe.get_doc("Sales Invoice", invoice)
                    party_name = doc.customer_name
                    if doc.total_taxes_and_charges:
                        igv, monto_impuesto, igv_inc = get_igv(company, invoice, doctype)
                    else:
                        igv = monto_impuesto = igv_inc = 0
                    if doc.customer_address:
                        address = get_address_information(doc.customer_address)
                    if doc.codigo_transaccion_sunat == "4":
                        advance = frappe.get_doc("Sales Invoice", doc.sales_invoice_advance)
                        monto_anticipo_neto = round(advance.net_total, 2)
                        anticipo_total = round(advance.grand_total)
                        igv_anticipo, anticipo_amount, anticipo_inc = get_igv(company, advance.name, doctype)
                    if doc.is_return == 1:
                        tipo, return_serie, return_correlativo = get_serie_correlativo(doc.return_against)
                        codigo_nota_credito = doc.codigo_nota_credito
                        return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
                        mult = -1
                    content = {
                        "operacion": "generar_comprobante",
                        "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_comprobante)),
                        "serie": serie,
                        "numero": correlativo,
                        "sunat_transaction": doc.codigo_transaccion_sunat,
                        "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                        "cliente_numero_de_documento": doc.tax_id,
                        "cliente_denominacion": party_name,
                        "cliente_direccion": address.address if address.get("address") else "",
                        "cliente_email": address.email if address.get("email") else "",
                        "cliente_email_1": "",
                        "cliente_email_2": "",
                        "fecha_de_emision": doc.get_formatted("posting_date"),
                        "fecha_de_vencimiento": doc.get_formatted("due_date"),
                        "moneda": str(get_moneda(doc.currency)),
                        "tipo_de_cambio": str(doc.conversion_rate),
                        "porcentaje_de_igv": str((igv - igv_anticipo) * mult),
                        "descuento_global": "",
                        "total_descuento": "",
                        "total_anticipo": str(monto_anticipo_neto) if not monto_anticipo_neto==0 else "",
                        "total_gravada": str(round(doc.net_total - monto_anticipo_neto, 2) * mult) if not igv==0 else "",
                        "total_inafecta": "",
                        "total_exonerada": str(round(doc.net_total - monto_anticipo_neto, 2) * mult) if igv==0 else "",
                        "total_igv": str(round(monto_impuesto - anticipo_amount, 2) * mult),
                        "total_gratuita": "",
                        "total_otros_cargos": "",
                        "total": str(round(doc.grand_total - anticipo_total, 2) * mult),
                        "percepcion_tipo": "",
                        "percepcion_base_imponible": "",
                        "total_percepcion": "",
                        "total_incluido_percepcion": "",
                        "detraccion": "false",
                        "observaciones": "",
                        "documento_que_se_modifica_tipo": return_type,
                        "documento_que_se_modifica_serie": return_serie,
                        "documento_que_se_modifica_numero": return_correlativo,
                        "tipo_de_nota_de_credito": str(codigo_nota_credito),
                        "tipo_de_nota_de_debito": "",
                        "enviar_automaticamente_a_la_sunat": "true",
                        "enviar_automaticamente_al_cliente": "true",
                        "codigo_unico": "",
                        "condiciones_de_pago": "",
                        "medio_de_pago": "",
                        "placa_vehiculo": "",
                        "orden_compra_servicio": "",
                        "tabla_personalizada_codigo": "",
                        "formato_de_pdf": ""
                    }
                    content['items'] = []
                    if doc.codigo_transaccion_sunat == "4":
                        advance_tipo, advance_serie, advance_correlativo = get_serie_correlativo(doc.sales_invoice_advance)
                        content['items'].append(
                            {
                                "unidad_de_medida": "NIU",
                                "codigo": "001",
                                "descripcion": "REGULARIZACIÓN DEL ANTICIPO",
                                "cantidad": "1",
                                "valor_unitario": str(round(doc.net_total, 2)),
                                "precio_unitario": str(round(doc.grand_total, 2) * mult),
                                "descuento": "",
                                "subtotal": str(round(doc.net_total, 2)),
                                "tipo_de_igv": "1" if not igv==0 else "8",
                                "igv": str(round(monto_impuesto, 2)),
                                "total": str(round(doc.grand_total, 2) * mult),
                                "anticipo_regularizacion": "false",
                                "anticipo_documento_serie": "",
                                "anticipo_documento_numero": ""
                            }),
                        content['items'].append({
                                "unidad_de_medida": "NIU",
                                "codigo": "001",
                                "descripcion": "PRIMER ANTICIPO",
                                "cantidad": "1",
                                "valor_unitario": str(monto_anticipo_neto),
                                "precio_unitario": str(anticipo_total),
                                "descuento": "",
                                "subtotal": str(monto_anticipo_neto),
                                "tipo_de_igv": "1" if not igv==0 else "8",
                                "igv": str(round(anticipo_amount, 2)),
                                "total": str(anticipo_total),
                                "anticipo_regularizacion": "true",
                                "anticipo_documento_serie": str(advance_serie),
                                "anticipo_documento_numero": str(advance_correlativo)
                            })
                    else:
                        for item in doc.items:
                            tipo_producto = get_tipo_producto(item.item_code)
                            content['items'].append({
                                "unidad_de_medida": tipo_producto,
                                "codigo": item.item_code,
                                "descripcion": item.item_name,
                                "cantidad": str(item.qty * mult),
                                "valor_unitario": str(round(item.net_rate, 2)),
                                "precio_unitario": str(round(item.rate, 2)) if igv_inc == 1 else str(round(item.net_rate, 2) * (1 + igv)),
                                "descuento": str(round(item.discount_amount, 2)) if (item.discount_amount > 0) else "",
                                "subtotal": str(round(item.net_amount, 2) * mult),
                                "tipo_de_igv": "1" if not igv==0 else "8",
                                "igv": str(round(item.net_amount * igv / 100, 2) * mult),
                                "total": str(round(item.amount, 2) * mult) if igv_inc == 1 else str(round(item.net_amount, 2) * mult * (1 + igv)),
                                "anticipo_regularizacion": "false",
                                "anticipo_documento_serie": "",
                                "anticipo_documento_numero": ""
                        })
                elif doctype == "Delivery Note":
                    doc = frappe.get_doc("Delivery Note", invoice)
                    doc_transportista = get_doc_transportista(doc.transporter)
                    doc_conductor = get_doc_conductor(doc.driver)
                    company_address = customer_address = {}
                    if doc.customer_address:
                        address = get_address_information(doc.customer_address)
                    if doc.shipping_address_name:
                        customer_address = get_address_information(doc.shipping_address_name)
                    else:
                        customer_address = address
                    if doc.company_address:
                        company_address = get_address_information((doc.company_address))
                    content = {
                        "operacion": "generar_guia",
                        "tipo_de_comprobante": "7",
                        "serie": serie,
                        "numero": correlativo,
                        "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                        "cliente_numero_de_documento": doc.tax_id,
                        "cliente_denominacion": doc.customer_name,
                        "cliente_direccion": address.getaddress if address.get('address') else "",
                        "cliente_email": address.email if address.get('email') else "",
                        "cliente_email_1": "",
                        "cliente_email_2": "",
                        "fecha_de_emision": doc.get_formatted("posting_date"),
                        "observaciones": "",
                        "motivo_de_traslado": doc.codigo_motivo_traslado,
                        "peso_bruto_total": doc.total_net_weight,
                        "numero_de_bultos": doc.numero_bultos if doc.numero_bultos else "0",
                        "tipo_de_transporte": doc.codigo_motivo_traslado,
                        "fecha_de_inicio_de_traslado": doc.get_formatted("lr_date"),
                        "transportista_documento_tipo": doc_transportista.codigo_tipo_documento,
                        "transportista_documento_numero": doc_transportista.tax_id,
                        "transportista_denominacion": doc_transportista.supplier_name,
                        "transportista_placa_numero": doc.vehicle_no,
                        "conductor_documento_tipo": doc_conductor.codigo_documento_identidad,
                        "conductor_documento_numero": doc_conductor.tax_id,
                        "conductor_denominacion": doc_conductor.full_name,
                        "punto_de_partida_ubigeo": company_address.ubigeo,
                        "punto_de_partida_direccion": company_address.address,
                        "punto_de_llegada_ubigeo": customer_address.ubigeo,
                        "punto_de_llegada_direccion": customer_address.address,
                        "enviar_automaticamente_a_la_sunat": "true",
                        "enviar_automaticamente_al_cliente": "false",
                        "codigo_unico": "",
                        "formato_de_pdf": "",
                    }
                    content['items'] = []
                    for item in doc.items:
                        tipo_producto = get_tipo_producto(item.item_code)
                        content['items'].append({
                            "unidad_de_medida": tipo_producto,
                            "codigo": item.item_code,
                            "descripcion": item.item_name,
                            "cantidad": str(item.qty)
                    })
                response = requests.post(url, headers=headers, data=json.dumps(content))
                data = json.loads(response.content)
            except:
                return ""
            else:
                return data
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def consult_document(company, invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            doc = frappe.get_doc(doctype, invoice)
            content = {
                "operacion": "consultar_comprobante",
                "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_tipo_comprobante if doctype == "Delivery Note" else doc.codigo_comprobante)),
                "serie": serie,
                "numero": correlativo
            }
            response = requests.post(url, headers=headers, data=json.dumps(content))
            return json.loads(response.content)
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def cancel_document(company, invoice, doctype, motivo):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            data = consult_document(company, invoice, doctype)
            if data.get("codigo_hash"):
                content = {
                    "operacion": "generar_anulacion",
                    "tipo_de_comprobante": data["tipo_de_comprobante"],
                    "serie": data["serie"],
                    "numero": data["numero"],
                    "motivo": motivo,
                    "codigo_unico": ""
                }
                response = requests.post(url, headers=headers, data=json.dumps(content))
                if doctype == "Sales Invoice":
                    frappe.db.sql(
                        """UPDATE `tabSales Invoice` SET estado_anulacion='En proceso', hora_cancelacion='{0}' WHERE name='{1}' and company='{2}'""".format(
                            datetime.datetime.now(), invoice, company))
                    frappe.db.commit()
                elif doctype == 'Delivery Note':
                    frappe.db.sql(
                        """UPDATE `tabDelivery Note` SET estado_anulacion='En proceso', hora_cancelacion='{0}' WHERE name='{1}' and company='{2}'""".format(
                            datetime.datetime.now(), invoice, company))
                    frappe.db.commit()
                return json.loads(response.content)
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def consult_cancel_document(company, invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            data = consult_document(company, invoice, doctype)
            if data.get("codigo_hash"):
                content = {
                    "operacion": "consultar_anulacion",
                    "tipo_de_comprobante": data["tipo_de_comprobante"],
                    "serie": data["serie"],
                    "numero": data["numero"]
                }
                response = requests.post(url, headers=headers, data=json.dumps(content))
                return json.loads(response.content)
        else:
            return ""
    else:
        return ""
