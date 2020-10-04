#!python3
import socketserver

def do_xor(data):
    key = b"\x10\x07\x19"
    return bytearray([data[i] ^ key[i%3] for i in range(len(data))])

def win():
    with open('flag.txt', 'r') as f:
        return f.read()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        s = self.request
        data = s.recv(1024)
        ddata = do_xor(data)
        print(b'from client : ', ddata)
        if ddata == b'Hell, World':
            s.send(do_xor(win().encode()))
        s.close()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    try:
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()
    except:
        server.server_close()