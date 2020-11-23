import socket
from http.server import HTTPServer
from socketserver import TCPServer
from socketserver import ThreadingMixIn


class UnixHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_UNIX

    def server_bind(self):
        TCPServer.server_bind(self)
        self.server_name = "foo"
        self.server_port = 0
