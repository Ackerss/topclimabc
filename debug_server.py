from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sys

class LoggerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("====== JAVASCRIPT LOG ======", flush=True)
        print(post_data.decode('utf-8'), flush=True)
        print("============================", flush=True)
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
        self.end_headers()

if __name__ == '__main__':
    server_address = ('', 8001)
    httpd = HTTPServer(server_address, LoggerHandler)
    print('Debug server on port 8001...', flush=True)
    httpd.serve_forever()
