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
