# simple_packet
### #socket #tcp #packet #forensic


![files](../../.images/simple_packet1.png)

파일은 총 3개가 주어진다.

- client.py  server.py
    
    두 파일은 소켓 통신을 한다. 
    ![server1](../../.images/simple_packet2.png)

    보다시피 server.py 는 localhost:9999 에 해당 소켓을 열어놓고 client.py 의 입력을 기다린다. 
    이 때, client.py 에서 온 data 는 **do_xor()** 함수를 통과하여 온다.

    **do_xor()** 함수는 server.py 와 client.py 에서 똑같은 형태인데, 통신과정에서 출제자가 커스텀으로 만든 인코딩 함수이다.


- simple_packet.pcapng