import mimetypes
import os
import socket

CRLF = '\r\n'

def mount_message(message):
    return f"{message}{CRLF}".encode("utf-8")


class HTTPRequest:

    def __init__(self, data):
        self._parse(data)

    def _parse(self, data):
        request_line = data.split(CRLF)[0].split(" ")
        if len(request_line) > 1:
            self.uri = request_line[1]
        if len(request_line) > 2:
            self.http_version = request_line[2]
        self.method = request_line[0]


class HTTPResponse:

    def __init__(self, status_code, headers, resbonse_body):
        self._response_line = self.response_line(status_code)
        self._response_headers = self.response_headers(headers)
        self._response_body = resbonse_body

    def response_line(self, status_code):
        responses_codes = {
            "200": "OK",
            "404": "Not Found",
            "501": "Not Implemented"
        }
        return f"HTTP/1.1 {status_code} {responses_codes[status_code]} {CRLF}".encode()

    def response_headers(self, extra_headers):
        headers = {}
        for key, value in extra_headers.items():
            headers[key] = value
        
        response = ""

        for key, value in headers.items():
            response += f"{key}:{value}{CRLF}"

        return response.encode()
    
    def __bytes__(self):
        return b"".join([self._response_line, self._response_headers, CRLF.encode(), self._response_body])

class TCPServer:
    default_headers = {
        'Content-Type': 'text/html',
    }
    
    default_html_response_file = "index.html"
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind(("localhost", 5000))
        server_socket.listen(5)
        while True:
            client, _ = server_socket.accept()
            data = client.recv(1024).decode()
            request = HTTPRequest(data)
            response = self.handle_request(request)
            client.sendall(bytes(response))
            client.close()            

    def handle_request(self, request:HTTPRequest):
        allowed_methods = {
            "GET": self.handle_get
        }
        return allowed_methods.get(request.method, self.handle_not_implemented)(request)
        

    def handle_get(self, request:HTTPRequest):
        filename = self.default_html_response_file
        filename = request.uri.strip("/") or self.default_html_response_file
        response_status = "200"
        response_body = ""
        headers = self.default_headers.copy()
        headers["Content-Type"] = mimetypes.guess_type(filename) or "text/html"
        if not os.path.exists(filename):
            response_status = "404"
            response_body = b"<h1>Not Found</h1>"
        else:
            with open(filename, "rb") as file:
                response_body = file.read()
        return HTTPResponse(
            response_status, 
            headers, 
            response_body
        )
    
    def handle_not_implemented(self,request:HTTPRequest):
        response_status = "501"
        response_body = b"<h1>Not Implemented</h1>"
        return HTTPResponse(
            response_status, 
            self.default_headers, 
            response_body
        )

    
def main():
    server = TCPServer()
    server.start()

if __name__ == "__main__":
    main()
