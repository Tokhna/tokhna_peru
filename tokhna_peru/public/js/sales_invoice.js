cur_frm.add_fetch('customer', 'codigo_tipo_documento', 'codigo_tipo_documento');
cur_frm.add_fetch('customer', 'tipo_documento_identidad', 'tipo_documento_identidad');
cur_frm.add_fetch('tipo_transaccion_sunat', 'codigo_tipo_transaccion', 'codigo_transaccion_sunat');
cur_frm.add_fetch('tipo_nota_credito', 'codigo_notas_credito', 'codigo_nota_credito');

function get_document_series(frm, cdt, cdn) {
	frappe.call({
		type: "GET",
		method: "tokhna_peru.tokhna_peru.doctype.configuracion.configuracion.get_doc_serie",
		args: {
            company: frm.doc.company,
			doctype: frm.doc.doctype,
			is_return: frm.doc.is_return ? "1" : "0",
			es_nota_debito: frm.doc.es_nota_debito ? "1" : "0",
			contingencia: frm.doc.contingencia ? "1" : "0",
			codigo_tipo_documento: frm.doc.codigo_tipo_documento
		},
		callback: function(r) {
			frappe.model.set_value(cdt, cdn, "tipo_comprobante", r.message.descripcion);
			frappe.model.set_value(cdt, cdn, "codigo_comprobante", r.message.codigo);
			frm.set_df_property("naming_series", "options", r.message.series);
		}
	});
}

function get_document_transaction(frm, cdt, cdn) {
	frappe.call({
		type: "GET",
		method: "tokhna_peru.tokhna_peru.doctype.tipos_de_transaccion_sunat.tipos_de_transaccion_sunat.get_tipo_transaccion",
		args: {
			customer: frm.doc.customer,
			is_return: frm.doc.is_return ? "1" : "0"
		},
		callback: function(r) {
			frappe.model.set_value(cdt, cdn, "tipo_transaccion_sunat", r.message.descripcion);
			frappe.model.set_value(cdt, cdn, "codigo_transaccion_sunat", r.message.codigo);
		}
	});
}

function get_product_anticipo(frm, cdt, cdn) {
	if (frm.doc.codigo_transaccion_sunat == "4") {
		frappe.call({
			type: "GET",
            method: "tokhna_peru.tokhna_peru.doctype.configuracion.configuracion.get_product_anticipo",
            args: {
                company: frm.doc.company
            },
			callback: function(r) {
				if (r.message) {
					if (frm.doc.sales_invoice_advance === undefined){
						cur_frm.set_query("item_code", "items", function(){
							return {
								"filters": [
									["Item", "name", "in", r.message]]
							};
						});
					}
					else {
						cur_frm.set_query("item_code", "items", function(){
							return {
								"filters": [
									["Item", "name", "!=", r.message]]
							};
						});
					}
					cur_frm.clear_table("items");
					frm.refresh_field("items");
				}
			}
		});
	}
	else {
		frappe.model.set_value(cdt, cdn, "sales_invoice_advance", "");
		cur_frm.toggle_display("sales_invoice_advance", false);
	}
}

function get_sales_invoice_advance(frm, cdt, cdn) {
	if (frm.doc.codigo_transaccion_sunat == "4") {
		cur_frm.set_query("sales_invoice_advance" , function(){
			return {
				"filters": [
				["Sales Invoice", "codigo_transaccion_sunat", "=", "4"],
				["Sales Invoice", "customer", "=", frm.doc.customer],
				["Sales Invoice", "sales_invoice_advance", "=", null]]
			};
		});
	}
	else {
		frappe.model.set_value(cdt, cdn, "sales_invoice_advance", "");
	}
}

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
		get_document_transaction(frm, cdt, cdn);
	});
}

function set_pos_profile(frm, cdt, cdn) {
	if (frm.doc.__islocal == 1 && frm.doc.naming_series != "" && frm.doc.customer != ""){
		frappe.db.get_list("POS Profile", {filters: {selling_price_list: frm.doc.selling_price_list, naming_series: frm.doc.naming_series}}).then(pos_profiles => {
			$.each(pos_profiles, function(i, row){
				frappe.db.get_doc("POS Profile", row.name).then(pos_profile => {
					$.each(pos_profile.applicable_for_users, function(i, row){
						console.log(pos_profile);
						if (row.user == frappe.session.user){
							frappe.model.set_value(cdt, cdn, "is_pos", 1);
							frappe.model.set_value(cdt, cdn, "pos_profile", pos_profile.name);
							frappe.model.set_value(cdt, cdn, "set_warehouse", pos_profile.warehouse);
							frm.refresh_fields();
						}
					});
				});
			});
		});
	}
}

cur_frm.page.add_action_item("Send Electronic Invoice", function() {
	frappe.call({
		method: "tokhna_peru.tokhna_peru.facturacion_electronica.send_invoice_email",
		args: {
			"company": cur_frm.doc.company,
			"invoice": cur_frm.doc.name
		}
	})
});

frappe.ui.form.on("Sales Invoice", {
	tipo_transaccion_sunat: function(frm, cdt, cdn){
		get_product_anticipo(frm, cdt, cdn);
		get_sales_invoice_advance(frm, cdt, cdn);
    },
    
    sales_invoice_advance: function(frm, cdt, cdn){
		get_product_anticipo(frm, cdt, cdn);
    },
    
    customer: function(frm, cdt, cdn) {
		if (frm.doc.codigo_tipo_documento) {
			get_document_series(frm, cdt, cdn);
            get_document_transaction(frm, cdt, cdn);
            set_pos_profile(frm, cdt, cdn);
		} else {
			frappe.model.set_value(cdt, cdn, "tipo_comprobante", null);
			frappe.model.set_value(cdt, cdn, "codigo_comprobante", null);
			frappe.model.set_value(cdt, cdn, "tipo_transaccion_sunat", null);
			frappe.model.set_value(cdt, cdn, "codigo_transaccion_sunat", null);
		}
    },
    
    naming_series: function(frm, cdt, cdn) {
		set_pos_profile(frm, cdt, cdn);
    },
    
    contingencia: function(frm, cdt, cdn) {
		if (frm.doc.codigo_tipo_documento && frm.doc.contingencia == 1) {
			get_document_series(frm, cdt, cdn);
		}
    },
    
    is_return: function(frm, cdt, cdn) {
		if (frm.doc.codigo_tipo_documento && frm.doc.is_return == 1) {
			get_document_series(frm, cdt, cdn);
		}
    },
    
    before_submit: function(frm, cdt, cdn) {
		if(!frm.doc.customer_address && frm.doc.codigo_tipo_documento != "-"){
            frappe.validated = false;
            frappe.throw("Customer Address is missing");
        }
        if (frm.doc.estado_sunat == null || frm.doc.is_return == 1) {
            return new Promise(function(resolve, reject) {
				frappe.call({
                    method: "tokhna_peru.tokhna_peru.facturacion_electronica.send_document",
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
				console.log(values);
                if (values.message){
                    if (values.message.data){
                        if (values.message.data.state_type_description == "Aceptado" || values.message.data.state_type_description == "Registrado"){
                            frappe.model.set_value(cdt, cdn, "estado_sunat", values.message.data.state_type_description);
                            frappe.model.set_value(cdt, cdn, "enlace_pdf", values.message.links.pdf.replace("downloads", "print").replace("pdf/", ""));
                            frappe.model.set_value(cdt, cdn, "codigo_hash_sunat", values.message.data.hash);
                            frappe.model.set_value(cdt, cdn, "external_id", values.message.data.external_id);
                            window.open(values.message.links.pdf.replace("downloads", "print").replace("pdf/", ""));
                            if (values.message.response) {
                                frappe.model.set_value(cdt, cdn, "respuesta_sunat", values.message.response.description);
                            }
                        } else {
                            frappe.validated = false;
                            frappe.throw(data.message.response.description);
                        }
                    } else {
                        frappe.validated = false;
                    }                    
                }   else {
                    frappe.validated = false;
                }
                
			});
        }
    },
    
    refresh: function(frm, cdt, cdn) {
		if (frm.doc.is_return == 1) {
			get_document_series(frm, cdt, cdn);
		}
		if (frm.doc.__islocal == 1){
			if (frm.doc.customer){
				get_document_customer(frm, cdt, cdn);
			}			
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
			console.log(values);
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
    },
    
    onload: function(frm, cdt, cdn) {
		if (frm.doc.codigo_qr_sunat === undefined && frm.doc.estado_sunat == "Aceptado") {
			frappe.model.set_value(cdt, cdn, "estado_sunat", null);
		}
	}
});