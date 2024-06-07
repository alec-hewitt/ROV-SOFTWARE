import logging
import socket

class TCP_SOCKET:

    def __init__(self, host_ip, host_port):
        self.logger = logging.getLogger(__name__)
        self.host_ip = host_ip
        self.host_port = host_port

    def try_bind_socket(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host_ip, self.host_port))
        s.listen()
        try:
            self.conn, self.addr = s.accept()
            self.logger.info(f"Connected by {self.addr}")
            s.settimeout(0.2)
            return True
        except TimeoutError:
            print("Surface connection timed out...")
            s.close()
            return False

    def send_packed(self, bytes) -> bool:
        try:
            self.conn.sendall(bytes)
            return 1
        except Exception as e:
            print("exception in TCP: {}".format(e))
            self.restart()
            return 0

    def recv_n_bytes(self, n_bytes):
        self.conn.settimeout(0.1)
        data = bytearray()
        while len(data) < n_bytes:
            try:
                packet = self.conn.recv(n_bytes - len(data))
            except Exception as e:
                print("exception in recv_n_bytes: {}".format(e))
                return None
            if not packet:
                return None
            data.extend(packet)
        return data

    def restart(self):
        self.close()
        self.try_bind_socket()

    def close(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except OSError:
            pass
