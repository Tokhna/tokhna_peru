// Copyright (c) 2020, Tokhna and contributors
// For license information, please see license.txt
frappe.provide("tokhna_peru.autenticacion")

frappe.ui.form.on('Autenticacion', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Autenticacion', {
	onload_post_render: function(frm) {
		tokhna_peru.autenticacion.check_mandatory_to_set_button(frm);	
	},

	ruta: function(frm) {
		tokhna_peru.autenticacion.check_mandatory_to_set_button(frm);	
	},

	token: function(frm) {
		tokhna_peru.autenticacion.check_mandatory_to_set_button(frm);	
	}
});

tokhna_peru.autenticacion.check_mandatory_to_set_button = function(frm) {
	if (frm.doc.ruta != "" && frm.doc.token != ""){
		frm.fields_dict.test_connection.$input.addClass("btn-primary");
	}
	else{
		frm.fields_dict.test_connection.$input.removeClass("btn-primary");
	}
};

tokhna_peru.autenticacion.check_mandatory_to_fetch = function(doc) {
	$.each(["ruta"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
	$.each(["token"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
};

frappe.ui.form.on('Autenticacion', 'test_connection', function(frm) {
	tokhna_peru.autenticacion.check_mandatory_to_fetch(frm.doc);
	frappe.call({
		method: "tokhna_peru.tokhna_peru.doctype.autenticacion.autenticacion.test_connection",
		args: {
			'url': frm.doc.ruta,
			'token': frm.doc.token
		},
		callback: function (data) {
			if (data.message.codigo === 10){
				frappe.throw(data.message.errors);
			}
			else{
				msgprint(__("Successful Connection"),__("Success"));
			}
        }
	});
});