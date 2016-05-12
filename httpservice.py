from multiprocessing import Process, current_process, freeze_support
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json

def listen(address, api, worker_pool=6):

    class _handler(BaseHTTPRequestHandler):
        def set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
        def do_HEAD(self):
            self.set_headers()
        
        def do_GET(self):
            self.set_headers()
            
        def do_POST(self):
            self.set_headers()
            data = self.rfile.read(int(self.headers['Content-Length']))
            self.rfile.close()
            result = api.handle(json.loads(data))
            json.dump(result, self.wfile)
            self.wfile.close()
            
        def log_message(self, format, *args):
            print(format % tuple(args))

    def _serve(server):
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

    server = HTTPServer(address, _handler)
    procs = []
    
    for i in xrange(worker_pool):
        p = Process(target=_serve, args=(server,))
        procs.append(p)
    
    for p in procs:
        p.start()
        
    for p in procs:
        try:
            p.join()
        except KeyboardInterrupt:
            p.join()
    server.socket.close()
