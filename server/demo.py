#!/usr/bin/python
#coding:utf-8

import struct
import datetime

from tornado.tcpserver import TCPServer
from tornado.ioloop  import IOLoop

from tcpserver.server import GPSServer

def message_pack(msg_type, message):
    msg_len = len(message)
    if msg_len + 3 <= 255:
        data = struct.pack(('!BB%ds' % msg_len), msg_len + 3, msg_type, message)
        data = struct.pack(('!BB%dsHBB' % len(data)), 0x78, 0x78, data, get_crc16(data), 13, 10)
    else:
        data = struct.pack(('!HB%ds' % msg_len), msg_len + 4, msg_type, message)
        data = struct.pack(('!BB%dsHBB' % len(data)), 0x79, 0x79, data, get_crc16(data), 13, 10)
    return data

def hex_str(data):
    hex_value = ''
    for pu in data:
        hex_value = hex_value + str((pu >> 4) & 0xF) + str(pu & 0xF)
    return hex_value

class MessageReceiver(object):
    def __init__(self, resolver):
        super(MessageReceiver, self).__init__()
        self.type = 0
        self.msg_length = 0
        self.msg = None
        self.serial = None
        self._head = None
        self._reserve_length = 0
        self._resolver = resolver

    def update_head(self, data):
        self._head = data

        if data[0] == 0x78 and data[1] == 0x78:
            self.type = 1
            self.msg_length = data[2] - 5
            self._reserve_length = self.msg_length + 5
        elif data[0] == 0x79 and data[1] == 0x79:
            self.type = 2
            self.msg_length = data[2] << 8 + data[3] - 5
            self._reserve_length = self.msg_length + 6
        else:
            self.type = 0
            self.msg_length = 0
            self._head = None
            return False

        return True

    def set_body(self, data):
        if self._head != None:
            self._head = self._head + data

            pack_struct = ('!HBB%ds2sHH' if self.type == 1 else '!HHB%ds2sHH') % self.msg_length
            _, length, msg_type, msg, serial, crc, stop = struct.unpack(pack_struct, self._head)

            print(length, msg_type, msg, serial, crc, stop)

            return self._resolver.resolve(msg_type, serial, msg)

        return None

class MessageResolver(object):
    def __init__(self, stream):
        super(MessageResolver, self).__init__()
        self._stream = stream
        self._type_map = {
            0x01: self.resolve_login,
            0x10: self.resolve_gps,
            0x13: self.resolve_heart,
            0x1F: self.resolve_settime,
        }

    def resolve(self, msg_type, serial, msg):
        fun = self._type_map.get(msg_type)
        if fun:
            fun(msg_type, serial, msg)
        return True

    def resolve_login(self, msg_type, serial, msg):
        print(msg)
        imei, device_no = struct.unpack('!8sH', msg[:10])
        imei = hex_str(imei)

        print('receive login', imei, device_no)

        data = message_pack(msg_type, serial)
        self._stream.write(data)

    def resolve_gps(self, msg_type, serial, msg):
        year, month, day, hour, minute, second, gps_info, longtitude, latitude, speed, gps_state = struct.unpack('!BBBBBBBLLBH', msg)
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)
        longtitude = longtitude / 30000
        longtitude = '%dº%f‘' % (longtitude // 60, longtitude % 60)
        latitude = latitude / 30000
        latitude = '%dº%f‘' % (longtitude // 60, longtitude % 60)

        print('receive gps', date_time, longtitude, latitude, speed)

    def resolve_heart(self, msg_type, serial, msg):
        device_info, battery, signal = struct.unpack('!BBB', msg[:3])
        heart_type = (device_info >> 2) & 0xF

        print('receive heart', heart_type, battery, signal)

        data = message_pack(msg_type, serial)
        self._stream.write(data)

    def resolve_settime(self, msg_type, serial, msg):
        year, month, day, hour, minute, second = struct.unpack('!BBBBBB', msg[:6])
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)

        print('receive settime', date_time)

        data = struct.pack('!LH2s', int(datetime.datetime.utcnow().timestamp()), 0, serial)
        data = message_pack(msg_type, data)
        self._stream.write(data)

class Connection(object):
    clients = set()
    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self._receiver = MessageReceiver(MessageResolver(stream))
        self.start()
    
    def start(self):
        print("A new user has entered the chat room.", self._address)

        # while True:
        # print(dir(self._stream))
        # self._stream.read_until(bytes('\n', 'utf-8'), self.broadcast_messages)
        self._stream.read_bytes(5, self.resolve_head)

    def resolve_head(self, data):
        if self._receiver.update_head(data):
            self._stream.read_bytes(self._receiver._reserve_length, self.resolve_data)

    def resolve_data(self, data):
        self._receiver.set_body(data)

        # 读取下一个数据包
        self._stream.read_bytes(5, self.resolve_head)
    
    def send_message(self, data):
        self._stream.write(data)
        
    def on_close(self):
        print("A user has left the chat room.", self._address)
        Connection.clients.remove(self)

class ChatServer(TCPServer):
    def handle_stream(self, stream, address):
        print("New connection :", address, stream)
        Connection(stream, address) 
        print("connection num is:", len(Connection.clients))


if __name__=="__main__":
    print("Server start ......")
    server = GPSServer()  
    server.listen(8001)  
    IOLoop.instance().start()
