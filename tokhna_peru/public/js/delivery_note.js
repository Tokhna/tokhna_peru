cur_frm.add_fetch('tipo_comprobante', 'codigo_tipo_comprobante', 'codigo_tipo_comprobante');
cur_frm.add_fetch('customer', 'codigo_tipo_documento', 'codigo_tipo_documento');
cur_frm.add_fetch('customer', 'tipo_documento_identidad', 'tipo_documento_identidad');
cur_frm.add_fetch('motivo_traslado', 'codigo_motivo_traslado', 'codigo_motivo_traslado');
cur_frm.add_fetch('tipo_transporte', 'codigo_tipo_transporte', 'codigo_tipo_transporte');
cur_frm.add_fetch('transporter', 'nombre_tipo_transporte', 'tipo_transporte');
cur_frm.add_fetch('transporter', 'codigo_tipo_transporte', 'codigo_tipo_transporte');

function get_document_customer(frm, cdt, cdn){
	return new Promise(function(resolve, reject) {
		if (frm.doc.customer){
			var values = frappe.db.get_doc("Customer", frm.doc.customer);
			resolve(values);
		}
	}).then(function(values) {
		frappe.model.set_value(cdt, cdn, "codigo_tipo_documento", values.codigo_tipo_documento);
		frappe.model.set_value(cdt, cdn, "tipo_documento_identidad", values.tipo_documento_identidad);
		frm.refresh_fields();
		get_document_series(frm, cdt, cdn);
	});
}

function filter_comprobantes(frm, cdt, cdn){
	cur_frm.set_query("tipo_comprobante", function(){
		return {
			"filters": [
				["Tipos de Comprobante", "codigo_tipo_comprobante", "in", ["09"]]]
		};
	});
}

function get_document_series(frm, cdt, cdn){
	frappe.call({
		type: "GET",
		method: "tokhna_peru.tokhna_peru.doctype.configuracion.configuracion.get_doc_serie",
		args: {
			company: frm.doc.company,
			doctype: frm.doc.doctype,
			codigo_comprobante: frm.doc.codigo_comprobante
		},
		callback: function(r) {
			frappe.model.set_value(cdt, cdn, "tipo_comprobante", r.message.descripcion);
			frappe.model.set_value(cdt, cdn, "codigo_tipo_comprobante", r.message.codigo);
			frm.set_df_property("naming_series", "options", r.message.series);
		}
	});
}

frappe.ui.form.on("Delivery Note", {
	onload: function(frm, cdt, cdn){
		filter_comprobantes(frm, cdt, cdn);
	},

	customer: function(frm, cdt, cdn) {
		if (frm.doc.codigo_tipo_documento){
			get_document_series(frm, cdt, cdn);
		}
		else {
			frappe.model.set_value(cdt, cdn, "tipo_comprobante", null);
			frappe.model.set_value(cdt, cdn, "codigo_comprobante", null);
		}
	},

	before_submit: function(frm, cdt, cdn) {
		if(!frm.doc.customer_address || !frm.doc.transporter || ! frm.doc.driver){
            frappe.validated = false;
            frappe.throw("Data is missing, please check");
        }
        if (frm.doc.estado_sunat == null || frm.doc.is_return == 1) {
            return new Promise(function(resolve, reject) {
				frappe.call({
                    method: "tokhna_peru.tokhna_peru.facturacion_electronica.consult_document",
                    args: {
                        'company': frm.doc.company,
                        'invoice': frm.doc.name,
                        'doctype': frm.doc.doctype
                    },
                    callback: function(values) {
                        resolve(values);
                    }
                });
			}).then(function(values) {
                if (values.message.codigo == "24"){
                    frappe.call({
                        method: "tokhna_peru.tokhna_peru.facturacion_electronica.send_document",
                        args: {
                            'company': frm.doc.company,
                            'invoice': frm.doc.name,
                            'doctype': frm.doc.doctype
                        },
                        callback: function(data) {
                            console.log(data);
                            if (data.message.aceptada_por_sunat) {
                                frappe.model.set_value(cdt, cdn, "estado_sunat", (data.message.aceptada_por_sunat) ? ("Aceptado") : ("Rechazado"));
                                frappe.model.set_value(cdt, cdn, "respuesta_sunat", data.message.sunat_description);
                                frappe.model.set_value(cdt, cdn, "codigo_qr_sunat", data.message.cadena_para_codigo_qr);
                                frappe.model.set_value(cdt, cdn, "codigo_hash_sunat", data.message.codigo_hash);
                            } else{
                                frappe.validated = false;
                                frappe.throw(data.message.errors);
                            }
                        }
                    });
                } else {
                    frappe.model.set_value(cdt, cdn, "estado_sunat", (values.message.aceptada_por_sunat) ? ("Aceptado") : ("Rechazado"));
                    frappe.model.set_value(cdt, cdn, "respuesta_sunat", values.message.sunat_description);
                    frappe.model.set_value(cdt, cdn, "codigo_qr_sunat", values.message.cadena_para_codigo_qr);
                    frappe.model.set_value(cdt, cdn, "codigo_hash_sunat", values.message.codigo_hash);
                }
			});
        }
	},

	refresh: function(frm, cdt, cdn) {
		if (frm.doc.customer){
			get_document_customer(frm, cdt, cdn);
		}
	},

	before_cancel: function(frm, cdt, cdn) {
		return new Promise(function(resolve, reject) {
			frappe.call({
				method: "tokhna_peru.tokhna_peru.facturacion_electronica.consult_document",
				args: {
					'company': frm.doc.company,
					'invoice': frm.doc.name,
					'doctype': frm.doc.doctype
				},
				callback: function(values) {
					resolve(values);
				}
			});
		}).then(function(values) {
			if (values.message.codigo != "24" && values.message != ""){
				if (frappe.datetime.get_day_diff(frm.doc.posting_date, frappe.datetime.get_today()) < 7 && frm.doc.estado_anulacion != "En proceso") {
					return new Promise(function(resolve, reject) {
						frappe.prompt([
								{ 'fieldname': 'motivo', 'fieldtype': 'Data', 'label': 'Motivo de la cancelacion', 'reqd': 1 }
							],
							function(values) {
								resolve(values);
							},
							'Cancelacion de Comprobante',
							'Anular'
						);
					}).then(function(values) {
						frappe.validated = false;
						frappe.call({
							method: "tokhna_peru.tokhna_peru.facturacion_electronica.cancel_document",
							args: {
								'company': frm.doc.company,
								'invoice': frm.docname,
								'doctype': frm.doctype,
								'motivo': values.motivo
							},
							callback: function(data) {
								frappe.msgprint("<b>Esperando respuesta de SUNAT</b>", 'Cancelación');
							}
						});
					});
				} else {
					frappe.validated = false;
					frappe.msgprint("<b>Documento no se puede anular o esta en proceso de anulación</b>", 'Cancelación');
				}
			} 
		});
	}
});