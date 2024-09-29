// Copyright (c) 2024, yazan and contributors
// For license information, please see license.txt

frappe.ui.form.on('HL7 Relative Data', {
	// refresh: function(frm) {

	// }
	main_doc_type: function(frm){
		frappe.model.with_doctype(frm.doc.main_doc_type, function() {
			var options = $.map(frappe.get_meta(frm.doc.main_doc_type).fields,
					function(d) {
					if(d.fieldname && frappe.model.no_value_type.indexOf(d.fieldtype)===-1) {
					return d.fieldname;
						}
					return null;
					}
				);
				 
				frm.set_df_property('system_field', 'options', options);
			});
	}
});
