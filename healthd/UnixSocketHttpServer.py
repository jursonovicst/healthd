import os
import socket
from http.server import HTTPServer
from socketserver import TCPServer
from socketserver import ThreadingMixIn


class UnixHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_UNIX

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = None

    def server_bind(self):
        TCPServer.server_bind(self)

        # change socket permissions
        os.chmod(self.server_address, 0o0660)  # TODO: fix mode parsing from arguments

        self.server_name = "healthd"
        self.server_port = 0
