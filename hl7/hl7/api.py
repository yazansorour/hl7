import frappe
from hl7apy.parser import parse_message, parse_segment, parse_segments, parse_fields, parse_component
from datetime import datetime, timedelta
from hl7apy.v2_4 import ST
from dotmap import DotMap
import pydicom
from hl7.hl7.utils.hl7_utill import HL7Utill
import json

class JsonObject:
    def __init__(self, data):
        self.__dict__ = data

@frappe.whitelist()
# Read HL7 message
def parseHL7Message(msgName):
    hs = frappe.get_doc('HL7 Settings', msgName)
    msgContents = HL7Utill.prepareMessageOptions(hs.hl7_template)
    return msgContents

@frappe.whitelist()
def hl7Response(msg, port):
    print('------------Wait-----------------------')
    print(len(msg.splitlines()))
    msgSeg = HL7Utill.getDictSegments(msg)
    mshSeg = parse_segment(msgSeg['MSH'])
    pidSeg = parse_segment(msgSeg['PID-1'])

    metaData = HL7Utill.extractMetadata(msgSeg['MSH'])
    
    hos_oid = metaData['facility_receiver']['oid']
    hl7_settings_list = frappe.db.get_list("HL7 Settings", filters={"hospital_oid": metaData['facility_receiver']['oid'], "message_type_code": metaData['message_type']['type'] + "^" + metaData['message_type']['code']}, fields=["name"])
    hl7_settings = frappe.get_doc('HL7 Settings', hl7_settings_list[0].name)

    # Create Patient
    if hl7_settings.action == "Create":
        doc_event = frappe.new_doc(hl7_settings.doctype_event)
        
    # Document Information
    elif hl7_settings.action == "Update":
        filters = {}
        if len(hl7_settings.filter_table) > 0:
            for row in hl7_settings.filter_table:
                if len(row.field.split("~")) > 1:
                    seg = parse_segment(msgSeg[row.segement])
                    field = getattr(seg, row.field.split("~")[0])
                    fieldar = field[int(row.field.split("~")[1]) - 1]
                    component = fieldar.children[int(row.component) - 1]
                    subComp = component.children[int(row.sub_component) - 1]
                    result = subComp
                    result = relative_result(result.value.value)
                    setattr(doc_event, row.value, result)
                    filters[row.value] = result
                else:
                    seg = parse_segment(msgSeg[row.segement])
                    field = getattr(seg, row.field.split("~")[0])
                    fieldar = field[0]
                    component = fieldar.children[int(row.component) - 1]
                    subComp = component.children[int(row.sub_component) - 1]
                    result = subComp
                    result = relative_result(result.value.value)
                    filters[row.value] = result
                    
        doc_list = frappe.db.get_list(hl7_settings.doctype_event, filters=filters, fields=["name"])
        if len(doc_list) > 0:
            doc_event = frappe.get_doc(hl7_settings.doctype_event, doc_list[0].name)

    if len(hl7_settings.mapping_table) > 0:
        for row in hl7_settings.mapping_table:
            if len(row.field.split("~")) > 1:
                seg = parse_segment(msgSeg[row.segement])
                field = getattr(seg, row.field.split("~")[0])
                fieldar = field[int(row.field.split("~")[1]) - 1]
                component = fieldar.children[int(row.component) - 1]
                subComp = component.children[int(row.sub_component) - 1]
                result = subComp
                result = relative_result(result.value.value,row.value)
                setattr(doc_event, row.value, result)
            else:
                seg = parse_segment(msgSeg[row.segement])
                field = getattr(seg, row.field.split("~")[0])
                fieldar = field[0]
                component = fieldar.children[int(row.component) - 1]
                subComp = component.children[int(row.sub_component) - 1]
                result = subComp
                result = relative_result(result.value.value , row.value)
                setattr(doc_event, row.value, result)

    # Create a new DocType
    if hl7_settings.action == "Create":
        doc_event.hospital_id = hl7_settings.hospital_id
        doc_event.insert()

    # Update Patient
    elif hl7_settings.action == "Update":
        doc_event.save()

def relative_result(result , fieldName):
    isRelativeData = frappe.db.get_list("HL7 Relative Data", filters={'Key': result,'system_field':fieldName}, fields=['name', 'value'])
    if len(isRelativeData) > 0:
        return isRelativeData[0].value
    return result

@frappe.whitelist()
def sendHL7Message(docType, docName, action):
    hl7_settings = None
    data = json.loads(docName)
    record = JsonObject(data)

    # Check HL7 Settings
    settings_list = frappe.db.get_list(
        'HL7 Settings',
        filters={'doctype_event': docType, 'workflow_state': 'Enabled', 'message_type': 'Sender', 'action': action, 'hospital_id': record.hospital_id},
        fields=['name', 'workflow_state', 'doctype_event'],
    )
    print("Getting HL7 Settings .....")
    
    # Check if this doctype has HL7 settings
    if len(settings_list) > 0:
        print("Found HL7 Settings ...")
        hl7_settings = frappe.get_doc("HL7 Settings", settings_list[0].name)
        connection_failed = False
        date_now = datetime.now()

        # HL7 Message Sequence
        hl7_seq = frappe.new_doc("Message Sequence")
        hl7_seq.doc_id = hl7_settings.doctype_event
        hl7_seq.insert(ignore_permissions=True)
        last_seq = hl7_seq.name

        # HL7 Logs object
        hl7_logs = frappe.new_doc("HL7 Logs")
        hl7_logs.hl7_settings = hl7_settings.name

        try:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((hl7_settings.ip_address, hl7_settings.port_number))
            hl7_logs.status = "Succeeded"
        except:
            connection_failed = True
            hl7_logs.status = "Failed"
            hl7_logs.error_message = 'Server connection failed!\nTry changing IP Address or Port Number.'
            hl7_logs.creation_date = date_now
            hl7_logs.insert(ignore_permissions=True)
        
        msgSeg = HL7Utill.getDictSegments(hl7_settings.hl7_template)

        if len(hl7_settings.mapping_table) > 0:
            for row in hl7_settings.mapping_table:
                if len(row.field.split("~")) > 1:
                    seg = parse_segment(msgSeg[row.segement])
                    field = getattr(seg, row.field.lower().split("~")[0])
                    fieldar = field[int(row.field.split("~")[1]) - 1]
                    component = fieldar.children[int(row.component) - 1]
                    subComp = component.children[int(row.sub_component) - 1]
                    result = subComp
                    result.value = getattr(record, row.value)
                    msgSeg[row.segement] = seg.value
                else:
                    seg = parse_segment(msgSeg[row.segement])
                    field = getattr(seg, row.field.lower())
                    fieldar = field[0]
                    component = fieldar.children[int(row.component) - 1]
                    subComp = component.children[int(row.sub_component) - 1]
                    result = subComp
                    if row.field.lower() == "msh_7":
                        today = datetime.now()
                        format = "%Y%m%d%H%M%S"
                        formatted_date = today.strftime(format)
                        result.value = str(formatted_date)
                    elif row.field.lower() == "msh_10":
                        result.value = last_seq
                    else:
                        result.value = getattr(record, row.value)
                    msgSeg[row.segement] = seg.value

        m = ''
        for index, (key, value) in enumerate(msgSeg.items()):
            m += value + '\r'
        
        message = parse_message(m)
        payload = b"\x0b" + message.value.encode() + b"\x1c\x0d"
        
        if not connection_failed:
            try:
                clientSocket.send(payload)
                while True:
                    response = clientSocket.recv(1000)
                    if response is not None:
                        hl7_logs.response = response
                        break

                clientSocket.close()
                hl7_logs.status = "Succeeded"
                hl7_logs.message = payload
                hl7_logs.creation_date = date_now
                hl7_logs.insert(ignore_permissions=True)
            except:
                hl7_logs.status = "Failed"
                hl7_logs.message = data
                hl7_logs.error_message = "Unexpected error has occurred!\nA required field could be missing."
                hl7_logs.creation_date = date_now
                hl7_logs.insert(ignore_permissions=True)