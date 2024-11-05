import socket
import sys
from hl7apy.parser import parse_message
import requests
import json
from datetime import datetime
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (sys.argv[1], int(sys.argv[2]))
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16000)
            #print('received {!r}'.format(data))
            if data:
                # TODO Parse Message
                final_msg = []
                ms = ''
                for m in data.split(b'\r'):
                    final_msg.append(m.decode('utf-8'))
                for f in final_msg:
                    if len(f) > 10:
                        ms += f + '\r'
                # Send Message to the RIS System 
                url = 'http://127.0.0.1/api/method/hl7.hl7.api.hl7Response'
                headers = {'Authorization': 'Basic ZjcwNTlmZDdiODNiMzc2OjFjY2U4MTc2NTVhZTgzNg=='}
                payload = {
                    'msg':ms,
                    'port': int(sys.argv[2]),
                }
                response = requests.request("POST" ,url , headers=headers,data=payload)
                # TODO wait the reponse from RIS 
                # if its okay send ok ack 
                # get the response error and send it 
                hl7Message = parse_message(ms)
                rec_date = datetime.now().strftime("%Y%m%d%H%M")
                # Extract sending and receiving information from hl7Message with default values if null
                sending_application = hl7Message.children[0].children[2].value or "DefaultSendingApp"
                sending_facility = hl7Message.children[0].children[3].value or "DefaultSendingFacility"
                receiving_application = hl7Message.children[0].children[4].value or "DefaultReceivingApp"
                receiving_facility = hl7Message.children[0].children[5].value or "DefaultReceivingFacility"

                # Extract message type and trigger event with default values if null
                #message_type = hl7Message.children[0].children[8].children[0].value or "ACK"  # e.g., "ACK"
                #trigger_event = hl7Message.children[0].children[8].children[1].value or "A08"  # e.g., "A08"
                if response.status_code == 200:
                    # Parse the message string to a dictionary
                    message_str = response.json().get('message', '{}')
                    metaData = json.loads(message_str)  # Ensure this is a dict

                    # Extract the fields with default values if they are missing
                    application_sender = metaData.get('application_sender', {}).get('name', 'DefaultAppSender')
                    facility_sender = metaData.get('facility_sender', {}).get('name', 'DefaultFacilitySender')
                    application_receiver = metaData.get('application_receiver', {}).get('name', 'DefaultAppReceiver')
                    facility_receiver = metaData.get('facility_receiver', {}).get('name', 'DefaultFacilityReceiver')
                    message_type = metaData.get('message_type', {}).get('type', 'ACK')
                    message_code = metaData.get('message_type', {}).get('code', 'A08')

                    # Get the current date and time in the required format
                    rec_date = datetime.now().strftime("%Y%m%d%H%M")

                    # Construct the ACK message based on the received metadata
                    ack = (
                        b"\x0b MSH|^~\\&|"
                        + bytes(application_sender, 'utf-8') + b"|"
                        + bytes(facility_sender, 'utf-8') + b"|"
                        + bytes(application_receiver, 'utf-8') + b"|"
                        + bytes(facility_receiver, 'utf-8') + b"|"
                        + bytes(rec_date, 'utf-8') + b"||"
                        + bytes(f"{message_type}^{message_code}", 'utf-8') + b"||T|2.3\rMSA|AA|"
                        + bytes('{}|OK'.format(hl7Message.children[0].children[8].value), 'utf-8')
                        + b" \x1c\x0d"
                    )
                    print("Sending ACK data back to the client:", ack)
                

                    connection.sendall(ack)  
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()

