// Copyright (c) 2024, yazan and contributors
// For license information, please see license.txt
var msgList = null;

frappe.ui.form.on('HL7 Settings', {
    refresh: function(frm , cdt , cdn) {
		if (frm.doc.hl7_template != null && frm.doc.hl7_template !== '') 
		{
			parseTemplateMessage(frm).then(() => {
				let segments = [];
				Object.entries(msgList).forEach(([key,value])=>{
					segments.push(key);
				})
				frm.fields_dict.mapping_table.grid.update_docfield_property(
				'segement',
				'options',
				[""].concat(segments)
				);
				frm.fields_dict.filter_table.grid.update_docfield_property(
					'segement',
					'options',
					[""].concat(segments)
				);
			})
			.catch(err => {
				console.error("Error occurred while parsing HL7 message:", err);
				frappe.msgprint({
					title: __('Error'),
					indicator: 'red',
					message: __('An error occurred while processing the HL7 message. Please try again later.')
				});
			});
		}
		if (frm.doc.doctype_event != '' && frm.doc.doctype_event != null)
		{
			getEventDoctypes(frm,cdt,cdn);
		}
    },
	doctype_event:function(frm,cdt,cdn){
		getEventDoctypes(frm,cdt,cdn);
	}
});
function parseTemplateMessage(frm) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: "hl7.hl7.api.parseHL7Message",
            args: {
                msgName: frm.doc.name
            },
            callback: function(r) {
                msgList = r.message;  // Assign the message to msgList
                resolve();  // Resolve the promise
            },
            error: function(err) {
                reject(err);  // Reject the promise on error
            }
        });
    });
}

frappe.ui.form.on('HL7 Mapping Table','segement',function(frm,cdt,cdn){
    var item = locals[cdt][cdn];
    var seg = item.segement;
	if(msgList != null){
		let fields = [];
		Object.entries(msgList[seg]).forEach(([key,value])=>{
			fields.push(key);
		});
		frm.fields_dict.mapping_table.grid.update_docfield_property(
		'field',
		'options',
		[""].concat(fields)
		);
		frm.fields_dict.filter_table.grid.update_docfield_property(
			'field',
			'options',
			[""].concat(fields)
		);
	}
    frm.refresh_field("mapping_table");
	frm.refresh_field("filter_table");
})

frappe.ui.form.on('HL7 Mapping Table','field',function(frm,cdt,cdn){
    var item = locals[cdt][cdn];
    var seg = item.segement;
	var field = item.field;
	if(msgList != null){
		let components = [];
		Object.entries(msgList[seg][field]).forEach(([key,value])=>{
			components.push(key);
		});
		frm.fields_dict.mapping_table.grid.update_docfield_property(
		'component',
		'options',
		[""].concat(components)
		);
		frm.fields_dict.filter_table.grid.update_docfield_property(
			'component',
			'options',
			[""].concat(components)
		);
	}
    frm.refresh_field("mapping_table");
	frm.refresh_field("filter_table");
})

frappe.ui.form.on('HL7 Mapping Table','component',function(frm,cdt,cdn){
    var item = locals[cdt][cdn];
    var seg = item.segement;
	var field = item.field;
	var component = item.component;
	if(msgList != null){
		frm.fields_dict.mapping_table.grid.update_docfield_property(
		'sub_component',
		'options',
		[""].concat(msgList[seg][field][component])
		);
		frm.fields_dict.filter_table.grid.update_docfield_property(
			'sub_component',
			'options',
			[""].concat(msgList[seg][field][component])
		);
	}
	frm.refresh_field("mapping_table");
    frm.refresh_field("filter_table");
})

frappe.ui.form.on('HL7 Mapping Table','target_doctype',function(frm,cdt,cdn){
   var item = locals[cdt][cdn];
   frappe.model.with_doctype(item.target_doctype, function() {
   var options = $.map(frappe.get_meta(item.target_doctype).fields,
		   function(d) {
		   if(d.fieldname && frappe.model.no_value_type.indexOf(d.fieldtype)===-1) {
		   return d.fieldname;
			   }
		   return null;
		   }
	   );
		
	   frm.fields_dict.mapping_table.grid.update_docfield_property(
			   'value',
			   'options',
			   [""].concat(options)
			   );
		frm.fields_dict.filter_table.grid.update_docfield_property(
			'value',
			'options',
			[""].concat(options)
		);
   });
   
   frm.refresh_field("mapping_table");
   frm.refresh_field("filter_table");
})

function getEventDoctypes(frm,cdt,cdn)
{
    frappe.model.with_doctype(frm.doc.doctype_event, function() {
    	var options = $.map(frappe.get_meta(frm.doc.doctype_event).fields,
    			function(d) {
    			if(d.fieldname && frappe.model.no_value_type.indexOf(d.fieldtype)===-1) {
    			        if(d.fieldtype == "Link")
    			        {
    			            return d.options;
    			        }
    		    }
    		  }
    		);
            options.push(frm.doc.doctype_event);
            
            frm.fields_dict['mapping_table'].grid.get_field("target_doctype").get_query = function(doc, cdt, cdn) {
            	return {
            		filters: {
            		    "name":['in',options]
            		}
            	}
            }
			frm.fields_dict['filter_table'].grid.get_field("target_doctype").get_query = function(doc, cdt, cdn) {
            	return {
            		filters: {
            		    "name":['in',frm.doc.doctype_event]
            		}
            	}
            }
    	});
}

function getRecords(frm)
{
      frappe.db.get_list(frm.doc.doctype_event,{fields:["name"]}).then(res => {
              var records = [""]
    		  res.forEach(function(item){
    		      records.push(item.name)
    		  }) 
    		  set_field_options("record", records)
      })
}