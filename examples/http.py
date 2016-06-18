##################
# http_client.py #
##################

import usocket
import ujson
try:
    import ussl
    SUPPORT_SSL = True
except ImportError:
    ussl = None
    SUPPORT_SSL = False

SUPPORT_TIMEOUT = hasattr(usocket.socket, 'settimeout')
CONTENT_TYPE_JSON = 'application/json'

class Response(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        self.encoding = 'utf-8'

    @property
    def text(self):
        content = self.content

        return str(content, self.encoding) if content else ''

    def close(self):
        if self.raw is not None:
            self._content = None
            self.raw.close()
            self.raw = None

    def json(self):
        return ujson.loads(self.text)

    def raise_for_status(self):
        if 400 <= self.status_code < 500:
            raise OSError('Client error: %s' % self.status_code)
        if 500 <= self.status_code < 600:
            raise OSError('Server error: %s' % self.status_code)

# Returns (line_as_string, buffer_remainder)
# Supports \n, \r and \r\n
def readline(buffer, encoding='utf-8'):
    i = buffer.find(b"\n")
    j = buffer.find(b"\r")
    if i == -1 and j == -1:
        return (str(buffer, encoding), b"")
    if i == -1:
        j = i
    else:
        if j != -1:
            i = min(i, j)

    line = str(buffer[:i], encoding)
    if j > -1 and buffer[i+1] == b"\n"[0]:
        i += 1
    remainder = buffer[i+1:]

    return line, remainder

# Adapted from upip
def request(method, url, json=None, timeout=None, headers=None):
    urlparts = url.split('/', 3)
    proto = urlparts[0]
    host = urlparts[2]
    urlpath = '' if len(urlparts) < 4 else urlparts[3]

    if proto == 'http:':
        port = 80
    elif proto == 'https:':
        port = 443
    else:
        raise OSError('Unsupported protocol: %s' % proto[:-1])

    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    if json is not None:
        content = ujson.dumps(json)
        content_type = CONTENT_TYPE_JSON
    else:
        content = None

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][4]

    sock = usocket.socket()

    if timeout is not None:
        assert SUPPORT_TIMEOUT, 'Socket does not support timeout'
        sock.settimeout(timeout)

    sock.connect(addr)

    if proto == 'https:':
        assert SUPPORT_SSL, 'HTTPS not supported: could not find ussl'
        sock = ussl.wrap_socket(sock)

    sock.send('%s /%s HTTP/1.0\r\nHost: %s\r\n' % (method, urlpath, host))

    if headers is not None:
        for header in headers.items():
            sock.send('%s: %s\r\n' % header)

    if content is not None:
        sock.send('content-length: %s\r\n' % len(content))
        sock.send('content-type: %s\r\n' % content_type)
        sock.send('\r\n')
        sock.send(content)
    else:
        sock.send('\r\n')

    # Consume the whole response
    buffer = b"";
    received = sock.recv(1024)
    while len(received) > 0:
        buffer += received
        received = sock.recv(1024)
    print("done", buffer)

    # Read status line
    line, buffer = readline(buffer)
    protover, status, msg = line.split(None, 2)

    # Skip headers
    line, buffer = readline(buffer)
    while line != '' and len(buffer) > 0:
        line, buffer = readline(buffer)

    # Return response object
    return Response(int(status), buffer)


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)

#######################
# end: http_client.py #
#######################

# Example
import network
import socket
import pyb

nic = network.CC3100()
nic.connect("<<SSID>>","<<PW>>")
while (not nic.is_connected()):
    nic.update()
    pyb.delay(100)

#r = get('http://bowerham.net/hello_badge')
#r = get('http://jsonplaceholder.typicode.com/users')
r = get('http://httpbin.org/ip')
r.raise_for_status()
print("Status", r.status_code)
print("content", r.text)  # r.content for raw bytes or r.json() for parsed content

