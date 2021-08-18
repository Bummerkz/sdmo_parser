from http.server import HTTPServer as BaseHttpServer, BaseHTTPRequestHandler
from queue import Queue
from threading import Thread


class HTTPServer(BaseHttpServer):
    def __init__(self, address, request_queue: Queue = None):
        super().__init__(address, Handler)
        self._requestQueue = Queue() if request_queue is None else request_queue
        self._thread = Thread(name='HTTPServer', target=self.serve_forever)

    def start_serve(self):
        self._thread.start()

    @property
    def queue(self):
        return self._requestQueue


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        request = self._parse_path()
        if isinstance(self.server, HTTPServer):
            self.server.queue.put(request)
        self.wfile.write(bytes('OK', "utf8"))
        return

    def _parse_path(self):
        request = self.path.split('?', 2)
        result = HTTPGetRequest(name=request[0])
        if len(request) > 1:  # has vars
            params = request[1].split('&')
            for param in params:
                var_name, var_val = param.split('=')
                result.set(var_name, var_val)
        return result


class HTTPGetRequest:
    def __init__(self, name=None, params: dict = None):
        self.name = name
        if params is None:
            self.params = {}
        else:
            self.params = params

    def set(self, var_name, var_val):
        self.params[var_name] = var_val

    def __repr__(self):
        return 'Name: %s, Params %s' % (self.name, str(self.params))
