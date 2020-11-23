import socket
from http.server import HTTPServer
from socketserver import TCPServer
from socketserver import ThreadingMixIn
import os


class UnixHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_UNIX

    def server_bind(self):
        TCPServer.server_bind(self)

        # change socket permissions
        os.chmod(self.server_address, 0o0770)

        self.server_name = "healthd"
        self.server_port = 0
