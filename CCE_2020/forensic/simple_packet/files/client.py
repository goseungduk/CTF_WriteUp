#!python3

from socket import *
import sys

def do_xor(data):
    key = b"\x10\x07\x19"
    return bytearray([data[i] ^ key[i%3] for i in range(len(data))])

if len(sys.argv) != 2:
    print('[-] usage : {} server'.format(sys.argv[0]))
    sys.exit(-1)

host = sys.argv[1]
s = socket(AF_INET, SOCK_STREAM)
s.connect((host, 9999))
userInput = input("input : ")
s.send(do_xor(userInput.encode()))
data = s.recv(1024)
dec = do_xor(data)
print(dec)
s.close()
