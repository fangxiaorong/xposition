#!/usr/bin/python
#coding:utf-8

import socket
import time
 
HOST = '127.0.0.1'    # The remote host
PORT = 8001           # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
 
s.sendall(b'xx\x11\x01\x08gYp\x11\x96u\x90\x10\x1c2\x01\x00\x07\xed\xc3\r\n') # 发送登陆信息
time.sleep(5)
data = s.recv(1024)
print('Received', repr(data))

s.sendall(b'xx\n\x13\x04\x06\x04\x00\x01\x00\x02\xa7-\r\n') # 发送心跳
time.sleep(5)
data = s.recv(1024)
print('Received', repr(data))

s.sendall(b'xx\r\x1f\x00\x00\x00\x00\x00\x00\x00\x01\x00\x03\xef_\r\n')
time.sleep(5)
data = s.recv(1024)
print('Received', repr(data))

 
time.sleep(10)
s.close()



# b'xx\x11\x01\x08gYp\x11\x96u\x90\x10\x1c2\x01\x00\x07\xed\xc3\r\n'
# xxxxx 12
# receive login 0867597011967590 4124
# b'xx\n\x13\x04\x06\x04\x00\x01\x00\x08\x08w\r\n'
# xxxxx 5
# receive heart 1 6 4
# b'xx\r\x1f\x00\x00\x00\x00\x00\x00\x00\x01\x00\t@\x05\r\n'
# xxxxx 8
# receive settime 2000-0-0 0:0:0
# b'xx\x1f\x81\x17\x00\x00\x00\x00SEEFN&&&&&&&&&&&&##\x00\x01\x00\n\x8a\x82\r\n'
# xxxxx 26
# 129 message handler is not set.
# b'xx!\x81\x19\x00\x00\x00\x00SEESOS:18851118840,,#\x00\x01\x00\x0b\xa90\r\n'
# xxxxx 28
# 129 message handler is not set.
# b'xx0\x81(\x00\x00\x00\x00SEETIME:0|0||||||||]|||||||]|||||||}\x00\x01\x00\x0c\x814\r\n'
# xxxxx 43
# 129 message handler is not set.
# b'xx0\x81(\x00\x00\x00\x00SEETIME:1|1||||||||]|||||||]|||||||}\x00\x01\x00\r\xc7,\r\n'
# xxxxx 43
# 129 message handler is not set.
# b'xx\x99\x81\x93\x00\x00\x00\x00CTRLPARAMS:GTIMER=0;TIMER=0,30;PWRLIMIT=0;RING=1;CALLMODE=2;SIMALM=0,0;BATALM=1,0;PWRONALM=1,0;PWROFFALM=1,0;BLINDALM=0,60,20,1;SOSALM=1,3#\x00\x00\x00\x02\x00\x0f)\x8b\r\n'
# xxxxx 148
# 129 message handler is not set.
# b'xx\r\x8b\x01\xcc\x00Q\xd7\x00<[\x00\x0eXZ\r\n'
# xxxxx 8
# 139 message handler is not set.
# b'xxd,\x12\x0b\x03\x02/\x13\x01\xcc\x00Q\xd7\x00<[9Q\xd7\x00\xd7\xd7=Q\xd7\x00\xd5/JQ\xd7\x00<\\KQ\xd7\x00;/NQ\xfa\x00$\x97WQ\xfa\x00JE\\\x01\x06\xc0\xf4\xe6\xcc\x0e\\2h\xd1\xbai\xed\xe8B\xf4\x83\xcd\xe3\xa6\x84D\xa4V\x02Y\x80\xebD~\x03\xc9\xf8\xd22J|\x03\xc9\xf8\xd22J\x00\x10\xa7\xcc\r\n'
# xxxxx 95
# 44 message handler is not set.
# b"xx-\x81'\x00\x00\x00\x00ALLGFENCES:1,0;2,0;3,0;4,0;5,0#\x00\x00\x00\x02\x00\x11\x00U\r\n"
# xxxxx 40
# 129 message handler is not set.
# b'xx\x1c\x81\x16\x00\x00\x00\x00W\x00H\x00I\x00T\x00E\x00:\x00#\x00\x00\x00\x00\x01\x00\x12\xc6x\r\n'
# xxxxx 23
# 129 message handler is not set.
# b'xx\x1e\x81\x18\x00\x00\x00\x00OK#AL#: No data!\x00\x00\x00\x02\x00\x13\x8b\xd3\r\n'
# xxxxx 25
# 129 message handler is not set.
