import socket

class Flask:
    """ This object represents a uFlask webserver.
        Data Members:
            views: a dict of all the views
    """

    def __init__(self):
        """"""
        self.views = {}

    def _read_headers(self, header_string):
        """ Reads headers from a string """
        #split headers into lines
        headers = header_string.split("\r\n")
        method, endpoint, http_ver = headers[0].split()

        header_dict = {}

        for header in headers[1:]:
            eq_index = header.find(":")
            key = header[:eq_index].strip()
            val = header[eq_index:].strip()
            header_dict[key] = val

        return method, endpoint, header_dict

    def _get_response_headers(self, status, headers=None):
        """Generates response headers from a status code"""
        if headers is None:
            headers = {}

        header_string = "HTTP/1.1 {}\r\n".format(status)

        for key, val in headers.items():
            header_string += (key + ":" + val + "\r\n")

        header_string += "\r\n"
        return header_string

    def _gen_response(self, endpoint, method):
        """Generate an http response from an endpoint"""
        for view in self.views.values():
            if view["rule"] == endpoint:
                if method in view["methods"]:
                    if method == "OPTIONS":
                        headers = {"Allow": ",".join(view["methods"])}
                        return self._get_response_headers("200 OK", headers)
                    else:
                        return self._get_response_headers("200 OK") + view["view_func"]() + "\r\n"
                else:
                    return self._get_response_headers("405")
        return self._get_response_headers("404 NOT FOUND")

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """ Adds a URL rule for routing """
        options[endpoint] = endpoint
        methods = options.pop("methods", None)

        if endpoint is None:
            endpoint = view_func.__name__

        if methods is None:
            methods = getattr(view_func, "methods", None) or ("GET",)
            methods =set(item.upper() for item in methods)
            methods |= {"OPTIONS"}

        self.views[endpoint] = {
            'rule': rule,
            "view_func": view_func,
            "methods": methods
        }


    def route(self, rule, **options):
        """ A decorator wrapping add_url_rule """
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator


    def run(self, **options):
        """ Run the web server """
        port = options.pop("port", 80)
        try:
            sock = socket.socket()
            sock.bind(("0.0.0.0", port))
            sock.listen(5)

            while True:
                conn, addr = sock.accept()
                data = conn.recv(1024).decode("UTF-8")

                header_end = data.find("\r\n\r\n")
                if not header_end == -1:
                    header_string = data[:header_end]
                    body = data[header_end:]
                else:
                    header_string = data

                method, endpoint, headers = self._read_headers(header_string)

                print("{} {}".format(method, endpoint))

                conn.send(self._gen_response(endpoint, method).encode('utf-8'))
                conn.close()
        except KeyboardInterrupt:
            print("Keyboard Interrupt")

        finally:
            print("Shutting down webserver")
            sock.close()
