# -*- coding: utf-8 -*-
# Copyright (c) 2015, seethersan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.desk.reportview

from tokhna_peru.tokhna_peru.utils import Utils, to_file


class LibroElectronicodeCompras(Utils):
	def get_purchase_invoices(self, year, periodo):
		purchase_invoice_list = []
		from_date, to_date = self.get_dates(year, periodo)

		purchase_invoices = frappe.db.sql("""select      
				CONCAT(DATE_FORMAT(IFNULL(bill_expiration_date,bill_date),'%Y%m'),'00') as periodo,
				REPLACE(purchase_invoice.name, '-', '') as cuo,
				'M2' as correlativo_asiento,
				DATE_FORMAT(IFNULL(bill_date,posting_date),'%d/%m/%Y') as fecha_emision,
				DATE_FORMAT(IFNULL(bill_expiration_date,posting_date),'%d/%m/%Y') as fecha_cancelacion,
				IF(LENGTH(codigo_comprobante) = 1,CONCAT('0',codigo_comprobante), codigo_comprobante) as tipo_comprobante,
				REPLACE(REPLACE(REPLACE(CONCAT('0',SUBSTRING(IFNULL(bill_series,'0000'),-3)),'A',"0"),"T","0"),"O","0") as serie_comprobante,
				"" as codigo_dua,
				SUBSTRING(IF(REPLACE(REPLACE(bill_no,"-",""),'S/N','01')<999,CONCAT('0000',REPLACE(REPLACE(bill_no,"-",""),'S/N','01')),REPLACE(REPLACE(bill_no,"-",""),'S/N','01')),-4) as numero_comprobante,
				"" as resumen_diario,
				codigo_tipo_documento as tipo_documento,
				tax_id as numero_documento,
				supplier_name as nombre_proveedor,
				base_net_total as base_imponible,
				taxes_and_charges_added as monto_impuesto,
				"" as base_imponible_exportacion,
				"" as monto_impuesto_exportacion,
				"" as base_imponible_no_gravada,
				"" as monto_impuesto_no_gravada,
				"" as valor_adquisicion_no_gravada,
				"" as monto_isc,
				"" as otros_conceptos,			
				grand_total as valor_adquisicion,
				IF(currency = 'SOL', 'PEN', currency) as moneda,
				SUBSTRING(conversion_rate,1,POSITION('.' in conversion_rate)+3)  as tipo_cambio,
				IF(is_return,(SELECT bill_date FROM `tabPurchase Invoice` WHERE name=return_against),"") as fecha_inicial_devolucion,
				IF(is_return,(SELECT codigo_comprobante FROM `tabPurchase Invoice` WHERE name=return_against),"") as tipo_devolucion,
				IF(is_return,(SELECT bill_series FROM `tabPurchase Invoice` WHERE name=return_against),"") as serie_devolucion,
				"" as dua,
				IF(is_return,(SELECT bill_no FROM `tabPurchase Invoice` WHERE name=return_against),"") as numero_devolucion,
				IF(is_return,posting_date,"") as fecha_devolucion,
				"" as detraccion,
				"" as marca_detraccion,
				"" as clasificacion_items,
				"" as contrato,
				"" as error_1,
				"" as error_2,
				"" as error_3,
				"" as error_4,
				'1' as indicador_pago,
				'0' as anotacion
			from
				`tabPurchase Invoice` purchase_invoice
			where bill_date > '"""+str(from_date)+"""' 
			and bill_date < '"""+str(to_date)+"""' 
			and docstatus = 1
			order by bill_date""", as_dict=True)

		for d in purchase_invoices:
			purchase_invoice_list.append({
				'periodo': d.periodo,
				'cuo': d.cuo,
				'correlativo_asiento': d.correlativo_asiento,
				'fecha_emision': d.fecha_emision,
				'fecha_cancelacion': d.fecha_cancelacion,
				'codigo_tipo_comprobante': d.tipo_comprobante,
				'serie_comprobante': d.serie_comprobante,
				'codigo_DUA': d.codigo_dua,
				'numero_comprobante': d.numero_comprobante,
				'resumen_diario': d.resumen_diario,
				'tipo_documento': d.tipo_documento,
				'numero_documento': d.numero_documento,
				'nombre_proveedor': d.nombre_proveedor,
				'base_imponible': d.base_imponible,
				'monto_impuesto': d.monto_impuesto,
				'base_imponible_exportacion': d.base_imponible_exportacion,
				'monto_impuesto_exportacion': d.monto_impuesto_exportacion,
				'base_imponible_no_gravada': d.base_imponible_no_gravada,
				'monto_impuesto_no_gravada': d.monto_impuesto_no_gravada,
				'valor_adquisicion_no_gravada': d.valor_adquisicion_no_gravada,
				'monto_isc': d.monto_isc,
				'otros_conceptos': d.otros_conceptos,
				'valor_adquisicion': d.valor_adquisicion,
				'moneda': d.moneda,
				'tipo_cambio': d.tipo_cambio,
				'fecha_inicial_devolucion': d.fecha_inicial_devolucion,
				'tipo_devolucion': d.tipo_devolucion,
				'serie_devolucion': d.serie_devolucion,
				'dua': d.dua,
				'numero_devolucion': d.numero_devolucion,
				'fecha_devolucion': d.fecha_devolucion,
				'detraccion': d.detraccion,
				'marca_detraccion': d.marca_detraccion,
				'clasificacion_items': d.clasificacion_items,
				'contrato': d.contrato,
				'error_1': d.error_1,
				'error_2': d.error_2,
				'error_3': d.error_3,
				'error_4': d.error_4,
				'indicador_pago': d.indicador_pago,
				'anotacion': d.anotacion
				})
		return purchase_invoice_list


	def export_libro_compras(self, year, periodo, ruc):
		tipo = "compras"
		data = self.get_purchase_invoices(year, periodo)
		codigo_periodo = self.ple_name(year, periodo)
		nombre = "LE"+str(ruc)+codigo_periodo+'00080100'+'00'+'1'+ ('1' if data else '0') +'1'+'1'
		nombre = nombre + ".txt"
		return to_file(data, tipo, nombre)


	def export_libro_compras_vacio(self, year, periodo, ruc):
		tipo = "compras"
		data = ""
		codigo_periodo = self.ple_name(year, periodo)
		nombre = "LE"+str(ruc)+codigo_periodo+'00080200'+'00'+'1'+'0'+'1'+'1'
		nombre = nombre + ".txt"
		return to_file(data, tipo, nombre)


