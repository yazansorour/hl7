# Copyright (c) 2024, yazan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os

class Hl7Listener(Document):
    def validate(self):
        if self.workflow_state == "Enabled":
            os.system(f'nohup python3 hl7_listeners/start_listener.py {self.ip_address} {self.port} & echo $! > hl7_listeners/pid/{self.name}.pid')
        if self.workflow_state == "Disabled":
           os.system(f'kill `cat hl7_listeners/pid/{self.name}.pid`  && rm -rf hl7_listeners/pid/{self.name}.pid')
