import socket
import sys
from hl7apy.parser import parse_message
import requests
import json

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
                url = 'http://192.168.5.67/api/method/hl7.hl7.api.hl7Response'
                headers = {'Authorization': 'Basic NTFhN2M0YjFlN2FjNWQ4OjFhZjdkNGQwZWI4Y2JjYQ=='}
                payload = {
                    'msg':ms,
                    'port': int(sys.argv[2]),
                }
                response = requests.request("POST" ,url , headers=headers,data=payload)
                # TODO wait the reponse from RIS 
                # if its okay send ok ack 
                # get the response error and send it 
                hl7Message = parse_message(ms)
                ack = b"\x0b MSH|^~\\&|HL7Listener|HL7Listener|SOMEAPP|SOMEAPP|20198151353||ACK^A08||T|2.3\rMSA|AA|" + bytes('{}|OK'.format(hl7Message.children[0].children[8].value), 'utf-8') + b" \x1c\x0d"
                print('sending data back to the client')
                connection.sendall(ack)  
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()

