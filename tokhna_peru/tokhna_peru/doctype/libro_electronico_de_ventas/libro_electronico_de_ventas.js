// Copyright (c) 2016, seethersan and contributors
// For license information, please see license.txt
frappe.provide("tokhna_peru.libro_electronico_de_ventas");

cur_frm.add_fetch('company', 'tax_id', 'ruc');

frappe.ui.form.on('Libro Electronico de Ventas', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Libro Electronico de Ventas', 'periodo', function(frm) {
	tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_set_button(frm);
	
});
frappe.ui.form.on('Libro Electronico de Ventas', 'ruc', function(frm) {
	tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_set_button(frm);
	
});
frappe.ui.form.on('Libro Electronico de Ventas', 'company', function(frm) {
	tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_set_button(frm);
});
tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_set_button = function(frm) {
	if (frm.doc.periodo && frm.doc.ruc) {
		frm.fields_dict.get_data.$input.addClass("btn-primary");
	}
	else{
		frm.fields_dict.get_data.$input.removeClass("btn-primary");
	}
}
tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_fetch = function(doc) {
	$.each(["periodo"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
	$.each(["company"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
}
frappe.ui.form.on("Libro Electronico de Ventas", "get_data", function(frm) {
	tokhna_peru.libro_electronico_de_ventas.check_mandatory_to_fetch(frm.doc);
	frappe.call({
		method: "export_libro_ventas",
		doc: frm.doc,
		args: {
			'periodo': frm.doc.periodo,
			'ruc': frm.doc.ruc,
			'year': frm.doc.year
		},
		callback: function (r){
			if (r.message){
				$(location).attr('href', "/api/method/tokhna_peru.tokhna_peru.utils.send_file_to_client?"+
				"file="+r.message.archivo+
				"&tipo="+r.message.tipo+
				"&nombre="+r.message.nombre);
			}
		}
	});
});
