# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import formatdate
from tokhna_peru.tokhna_peru.doctype.autenticacion.autenticacion import get_autentication, get_url
from tokhna_peru.tokhna_peru.doctype.configuracion.configuracion import get_unaffected_config
from tokhna_peru.tokhna_peru.utils import get_serie_correlativo, get_moneda, get_igv, get_tipo_producto, get_serie_online, get_doc_conductor, get_doc_transportista, get_address_information, get_ibp
import requests
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def send_document(company, invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie + "-")
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            return_type = return_serie = return_correlativo = codigo_nota_credito = party_name = ""
            address = {}
            if frappe.db.exists("Electronic Invoice Request", invoice):
                request = frappe.get_doc("Electronic Invoice Request", invoice)
                response = json.loads(request.response)
                if response.get('success'):
                    return response
            try:
                if doctype == "Sales Invoice":
                    mult  = 1
                    monto_anticipo_neto = igv_anticipo = anticipo_amount = anticipo_total = 0
                    doc = frappe.get_doc("Sales Invoice", invoice)
                    party_name = doc.customer_name
                    if doc.total_taxes_and_charges:
                        igv, monto_impuesto, igv_inc = get_igv(company, invoice, doctype)
                        ibp, monto_ibp, ibp_inc = get_ibp(company, invoice, doctype)
                    else:
                        igv = monto_impuesto = igv_inc = 0
                        ibp = monto_ibp = ibp_inc = 0
                        if igv == 0 and get_unaffected_config(company) != 1:
                            return ""
                    if doc.customer_address:
                        address = get_address_information(doc.customer_address)
                    if doc.codigo_transaccion_sunat == "4":
                        advance = frappe.get_doc("Sales Invoice", doc.sales_invoice_advance)
                        monto_anticipo_neto = round(advance.net_total, 2)
                        anticipo_total = round(advance.grand_total)
                        igv_anticipo, anticipo_amount, anticipo_inc = get_igv(company, advance.name, doctype)
                        tipo_anticipo, serie_anticipo, correlativo_anticipo = get_serie_correlativo(doc.sales_invoice_advance)
                    if doc.is_return == 1:
                        tipo, return_serie, return_correlativo = get_serie_correlativo(doc.return_against)
                        codigo_nota_credito = doc.codigo_nota_credito
                        return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
                        mult = -1
                    content = {
                        "serie_documento": serie,
                        "numero_documento": int(correlativo),
                        "fecha_de_emision": formatdate(doc.get("posting_date"), "yyyy-mm-dd"),
                        "hora_de_emision": doc.get_formatted("posting_time"),
                        "codigo_tipo_operacion": "0101",
                        "codigo_tipo_documento": doc.codigo_comprobante,
                        "codigo_tipo_moneda": doc.currency,
                        "fecha_de_vencimiento": formatdate(doc.get("due_date"), "yyyy-mm-dd"),
                        "numero_orden_de_compra": doc.po_no or "",
                        "datos_del_cliente_o_receptor": {
                            "codigo_tipo_documento_identidad": doc.codigo_tipo_documento,
                            "numero_documento": doc.tax_id,
                            "apellidos_y_nombres_o_razon_social": party_name,
                            "codigo_pais": address.get("pais"),
                            "ubigeo": address.get("ubigeo", "") or "",
                            "direccion": address.get("address", ""),
                            "correo_electronico": address.get("email"),
                            "telefono": address.get("phone", "")
                        },
                        "totales": {
                            "total_exportacion": 0.00,
                            "total_operaciones_gravadas": float(round(doc.net_total - monto_anticipo_neto, 2) * mult) if not igv==0 else 0.00,
                            "total_operaciones_inafectas": float(round(doc.net_total - monto_anticipo_neto, 2) * mult) if igv==0 else 0.00,
                            "total_operaciones_exoneradas": 0.00,
                            "total_operaciones_gratuitas": 0.00,
                            "total_igv": float(round(monto_impuesto - anticipo_amount, 2) * mult),
                            "total_impuestos_bolsa_plastica": float(round(monto_ibp, 2) * mult),
                            "total_impuestos": float(round(monto_impuesto - anticipo_amount, 2) * mult),
                            "total_valor": float(round(doc.net_total - monto_anticipo_neto, 2) * mult),
                            "total_venta": float(round(doc.grand_total - anticipo_total, 2) * mult)
                        },
                    }
                    content['items'] = []
                    for item in doc.items:
                        tipo_producto = get_tipo_producto(item.item_code)
                        content['items'].append({
                            "codigo_interno": item.item_code.replace('-',''),
                            "descripcion": item.item_name,
                            "codigo_producto_sunat": frappe.get_value("Item", item.item_code, "codigo_sunat") or "",
                            "unidad_de_medida": tipo_producto,
                            "cantidad": float(item.qty * mult),
                            "valor_unitario": float(round(item.net_rate, 2)),
                            "codigo_tipo_precio": "01",
                            "precio_unitario": float(round(item.rate, 2)) if igv_inc == 1 else float(round(item.net_rate, 2) * (1 + igv)),
                            "codigo_tipo_afectacion_igv": "10" if not igv==0  else "30",
                            "total_base_igv": float(round(item.net_amount, 2) * mult),
                            "porcentaje_igv": 18,
                            "total_igv": float(round(item.net_amount * igv / 100, 2) * mult),
                            "total_impuestos": float(round(item.net_amount * igv / 100, 2) * mult),
                            "total_valor_item": float(round(item.net_amount, 2) * mult),
                            "total_item": float(round(item.amount, 2) * mult) if igv_inc == 1 else float(round(item.net_amount, 2) * mult * (1 + igv)),
                    })
                    if doc.codigo_comprobante == "07":
                        content['codigo_tipo_nota'] = doc.codigo_nota_credito
                        content['motivo_o_sustento_de_nota'] = doc.tipo_nota_credito
                        content['documento_afectado'] = {
                            "external_id": doc.external_id
                        }
                    if frappe.get_value("Configuracion", company, "invoice_format"):
                        content["acciones"] = { 
                            "formato_pdf": frappe.get_value("Configuracion", company, "invoice_format")
                        }
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
                    company_address = get_address_information(doc.company_address)
                    content = {
                        "serie_documento": serie,
                        "numero_documento": correlativo,
                        "fecha_de_emision": formatdate(doc.get("posting_date"), "yyyy-mm-dd"),
                        "hora_de_emision": doc.get_formatted("posting_time"),
                        "codigo_tipo_documento": "09",
                        "datos_del_emisor": {
                            "codigo_pais": company_address.pais,
                            "ubigeo": company_address.ubigeo,
                            "direccion": company_address.address,
                            "correo_electronico": company_address.email,
                            "telefono": address.get("phone", ""),
                            "codigo_del_domicilio_fiscal": address.get("code", "")
                        },
                        "datos_del_cliente_o_receptor":{
                            "codigo_tipo_documento_identidad": doc.codigo_tipo_documento,
                            "numero_documento": doc.tax_id,
                            "apellidos_y_nombres_o_razon_social": doc.customer_name,
                            "nombre_comercial": doc.customer_name,
                            "codigo_pais": customer_address.pais,
                            "ubigeo": customer_address.ubigeo,
                            "direccion": customer_address.address,
                            "correo_electronico": customer_address.email,
                            "telefono": customer_address.phone
                        },
                        "observaciones": "aaaaaaaaaaaaaaa",
                        "codigo_modo_transporte": doc.codigo_tipo_transporte,
                        "codigo_motivo_traslado": doc.codigo_motivo_traslado,
                        "descripcion_motivo_traslado": "El cliente solicito envia a su trabajo en ...",
                        "fecha_de_traslado": doc.get_formatted("lr_date"),
                        "codigo_de_puerto": "",
                        "indicador_de_transbordo": False,
                        "unidad_peso_total": "KGM",
                        "peso_total": doc.total_net_weight,
                        "numero_de_bultos": doc.numero_bultos,
                        "numero_de_contenedor": "",
                        "direccion_partida": {
                            "ubigeo": company_address.ubigeo,
                            "direccion": company_address.address
                        },
                        "direccion_llegada": {
                            "ubigeo": customer_address.ubigeo,
                            "direccion": customer_address.address
                        },
                        "transportista": {
                            "codigo_tipo_documento_identidad": doc_transportista.codigo_tipo_documento,
                            "numero_documento": doc_transportista.tax_id,
                            "apellidos_y_nombres_o_razon_social": doc_transportista.supplier_name
                        },
                        "chofer": {
                            "codigo_tipo_documento_identidad": doc_conductor.codigo_documento_identidad,
                            "numero_documento": doc_conductor.tax_id
                        },
                        "numero_de_placa": doc.vehicle_no,
                    }
                    content['items'] = []
                    for item in doc.items:
                        tipo_producto = get_tipo_producto(item.item_code)
                        content['items'].append({
                            "codigo_interno": item.item_code,
                             "cantidad": item.qty
                    })
                if frappe.get_value("Configuracion", company, "send_email_invoice") == 1:
                    if content.get("acciones"):
                        content["acciones"]["enviar_email"] = "true"
                    else:
                        content["acciones"] = { 
                            "enviar_email": "true"
                        }                
                request_date = datetime.strptime(formatdate(doc.get("posting_date"), "yyyy-mm-dd"), '%Y-%m-%d')
                today = datetime.today()
                if request_date.year == today.year and request_date.month == today.month:
                    data = json.loads(response.content)
                    if request:
                        request.request = json.dumps(content)
                        request.response = response.content
                        request.date = request_date
                        request.save(ignore_permissions=True)
                    else:
                        response = requests.post(url, headers=headers, data=json.dumps(content))
                        request = frappe.get_doc({
                            "doctype": "Electronic Invoice Request",
                            "sales_invoice": invoice,
                            "date": request_date,
                            "request": json.dumps(content),
                            "response": response.content
                        })
                        request.save(ignore_permissions=True)
                else:
                    return ""
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
                "tipo_de_comprobante": str(doc.codigo_tipo_comprobante if doctype == "Delivery Note" else doc.codigo_comprobante),
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
    online = get_serie_online(company, tipo + "-" + serie + "-")
    if online:
        url = get_url(company).replace('documents','voided')
        headers = get_autentication(company)
        if url != "" and headers != "":
            doc = frappe.get_doc("Sales Invoice", invoice)
            if doc.get("external_id"):
                content = {
                "fecha_de_emision_de_documentos": formatdate(doc.get_formatted("posting_date"), "yyyy-mm-dd"),
                "documentos": [
                        {
                        "external_id": doc.external_id,
                        "motivo_anulacion": motivo
                        }
                    ]
                }
                if doc.codigo_tipo_documento != "6":
                    content["codigo_tipo_proceso"] = "3"
                    url = get_url(company).replace('documents','summaries')
                response = requests.post(url, headers=headers, data=json.dumps(content))
                json_response = json.loads(response.content)
                if json_response.get('success'):
                    if doctype == "Sales Invoice":
                        frappe.db.sql(
                            """UPDATE `tabSales Invoice` SET estado_anulacion='En proceso', hora_cancelacion='{0}', anulacion_ticket='{1}', anulacion_external_id='{2}' WHERE name='{3}' and company='{4}'""".format(
                                datetime.now(), json_response.get('data').get('ticket'), json_response.get('data').get('external_id'), invoice, company))
                        frappe.db.commit()
                    elif doctype == 'Delivery Note':
                        frappe.db.sql(
                            """UPDATE `tabDelivery Note` SET estado_anulacion='En proceso', hora_cancelacion='{0}', anulacion_ticket='{1}', anulacion_external_id='{2}' WHERE name='{3}' and company='{4}'""".format(
                                datetime.now(), json_response.get('data').get('ticket'), json_response.get('data').get('external_id'), invoice, company))
                        frappe.db.commit()
                return json_response
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def consult_cancel_document(company, invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company).replace('documents','voided/status')
        headers = get_autentication(company)
        if url != "" and headers != "":
            doc = frappe.get_doc(doctype, invoice)
            if doc.get("estado_anulacion") == "En proceso":
                content = {
                    "external_id": doc.get('external_id'),
                    "ticket": doc.get('anulacion_ticket')
                }
                response = requests.post(url, headers=headers, data=json.dumps(content))
                return json.loads(response.content)
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def send_invoice_email(company, invoice):
    if frappe.get_value("Configuracion", company, "send_email_invoice_erpnext") == 1:
        doc = frappe.get_doc("Sales Invoice", invoice)
        customer_email = frappe.get_value("Address", doc.customer_address, "email_id")
        if customer_email and doc.enlace_pdf:
            frappe.sendmail(recipients=customer_email,subject="Comprobante Electrónico " + doc.name + " - COLEGIO PIONERO",
                message="Estimado/a usuario le adjuntamos su comprobante electrónico " + doc.enlace_pdf, delayed=False)

def validate_default_fields(doc, method=None):
    company = frappe.get_doc("Company", doc.company)
    income_account = company.get('default_income_account')
    cost_center = company.get('round_off_cost_center')
    for item in doc.items:
        if item.cost_center != cost_center:
            item.cost_center = cost_center
        if item.income_account != income_account:
            item.income_account = income_account