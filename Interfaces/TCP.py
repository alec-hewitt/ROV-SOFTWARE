import logging
import socket

class TCP_SOCKET:

    def __init__(self, host_ip, host_port):
        self.logger = logging.getLogger(__name__)
        self.host_ip = host_ip
        self.host_port = host_port

    def try_bind_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host_ip, self.host_port))
            s.listen()
            self.conn, self.addr = s.accept()
            self.logger.info(f"Connected by {self.addr}")

    def send_packed(self, bytes):
        try:
            self.conn.sendall(bytes)
        except Exception as e:
            print("exception in TCP: {}".format(e))
            self.restart()

    def recieve(self, n_bytes):
        if self.conn is None:
            raise RuntimeException
        with self.conn:
            data = conn.recv(n_bytes)
            print(data)
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
