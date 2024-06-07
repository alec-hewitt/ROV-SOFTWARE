import logging
import json
from Interfaces.TCP import TCP_SOCKET
import struct

class Surface:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.socket = TCP_SOCKET(host_ip = "192.168.1.12", host_port = 65432)
        self.connected = False

    def open_connection(self) -> bool:
        if self.connected == False:
            self.logger.info('Attemping to bind to client')
            self.connected = self.socket.try_bind_socket()
        return self.connected

    def pack_heartbeat(self, hb_dict, log: bool = False):
        with open("hb_packed.json" , "w") as outfile:
            json.dump(hb_dict, outfile)
            if log:
                self.logger.debug(hb_dict)

    def send_heartbeat(self):
        if self.connected:
            fi = open("hb_packed.json", "r")
            data = fi.read()
            self.logger.debug("packed struct: {}".format(struct.pack('>s', bytes(str(len(data)), 'utf-8') + bytes(data, 'utf-8'))))
            msg = struct.pack('>I', len(data)) + bytes(data, 'utf-8')
            if self.socket.send_packed(msg) == 0:
                fi.close()
                self.connected = False
            fi.close()
            return 1
        return 0

    def get_message(self):
        if self.connected:
            raw_msglen = self.socket.recv_n_bytes(4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            msg = self.socket.recv_n_bytes(msglen)
            if msg == None:
                self.connected = False
            self.logger.debug('Message from surface: {}'.format(msg))
            return msg

    def close(self):
        self.socket.close()
