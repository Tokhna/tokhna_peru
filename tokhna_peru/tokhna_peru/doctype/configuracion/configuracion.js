// Copyright (c) 2020, Tokhna and contributors
// For license information, please see license.txt

frappe.ui.form.on('Configuracion', {
	setup: function(frm) {
		frm.set_query("igv", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("percepcion", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("anticipo", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});
	}
});

frappe.ui.form.on('Detalle Configuracion Series', {
	'tipo_documento': function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function(r) {
				if (row.tipo_documento != "Guía de Remisión"){
					frappe.meta.get_docfield(cdt, 'serie_documento', frm.doc.name).options = r.message['venta'];
					frm.refresh_fields();
				} else {
					frappe.meta.get_docfield(cdt, 'serie_documento', frm.doc.name).options = r.message['guia'];
					frm.refresh_fields();
				}
			}
		});
	}
})
