import logging
import json
from Interfaces.TCP import TCP_SOCKET
import struct

class Surface:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.socket = TCP_SOCKET(host_ip = "192.168.1.12", host_port = 65432)

    def open_connection(self):
        self.logger.info('Attemping to bind to client')
        self.socket.try_bind_socket()
        self.logger.info('Done bind to client')

    def pack_heartbeat(self, hb_dict, log: bool = False):
        with open("hb_packed.json" , "w") as outfile:
            json.dump(hb_dict, outfile)
            if log:
                self.logger.debug(hb_dict)

    def send_heartbeat(self):
        fi = open("hb_packed.json", "r")
        data = fi.read()
        print("packed struct: {}".format(struct.pack('>s', bytes(str(len(data), 'utf-8') + data))))
        msg = struct.pack('>I', len(data)) + bytes(data, 'utf-8')
        self.socket.send_packed(msg)
        fi.close()

    def get_command(self):
        

    def close(self):
        self.socket.close()
