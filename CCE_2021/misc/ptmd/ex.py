from pwn import *
import operator


def calc(s, d):
    a = int(d[0])
    b = int(d[2])
    res = float(d[4])
    if(operator.mod(res, 1) > 0):
        s.send(b"/")
        return 0
    elif(operator.add(a, b) == res):
        s.send(b"+")
    elif(operator.sub(a, b) == res):
        s.send(b"-")
    else:
        s.send(b"*")


if __name__ == '__main__':
    # while(True):
    s = remote("20.194.123.97", 11111)
    s.recvuntil(
        b"/\n----------------------------------------------------------------------\n")
    # try:
    for i in range(0, 100):
        print(s.recvuntil(b"\n"))  # stage n
        d = s.recvuntil(b"\n")[:-1].decode().split(" ")
        calc(s, d)
