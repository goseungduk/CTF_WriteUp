import sys
from Crypto.Cipher import AES
import base64
prob='FyRyZNBO2MG6ncd3hEkC/yeYKUseI/CxYoZiIeV2fe/Jmtwx+WbWmU1gtMX9m905'
key1="SECCON"
key2="seccon2019"
key=key2+chr(0x00)*(16-(len(key2)%16))
cipher=AES.new(key,AES.MODE_ECB)

enc2=base64.b64decode(prob.encode('cp949'))
# to unicode
before_enc2=cipher.decrypt(enc2)
print(before_enc2)
# this is equal to enc1+chr(p)*p
# p=0x05
#print("________ we get 'p' = 0x05 ________")
enc1="'jff~|Ox9'34G9#g52F?489>B%|)173~)%8.'jff~|Q"
#print(enc1)
flag=''
for i in range(len(enc1)):
        tmp=chr((((ord(enc1[i])-0x20)+(0x7e-0x20+1))-(ord(key1[i%6])-0x20))+0x20)
        if(ord(tmp)>127):
                flag+=chr(ord(tmp)-95)
        else:
                flag+=tmp
print(flag)