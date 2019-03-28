#!/usr/bin/python
#coding:utf-8

import struct

from libs import crc_encode


# FORMAT  C TYPE  PYTHON TYPE STANDARD SIZE   NOTES
# x   pad byte    no value         
# c   char    string of length 1  1    
# b   signed char integer 1   (3)
# B   unsigned char   integer 1   (3)
# ?   _Bool   bool    1   (1)
# h   short   integer 2   (3)
# H   unsigned short  integer 2   (3)
# i   int integer 4   (3)
# I   unsigned int    integer 4   (3)
# l   long    integer 4   (3)
# L   unsigned long   integer 4   (3)
# q   long long   integer 8   (2), (3)
# Q   unsigned long long  integer 8   (2), (3)
# f   float   float   4   (4)
# d   double  float   8   (4)
# s   char[]  string       
# p   char[]  string       
# P   void *  integer     (5), (3)

class Message(object):
    MSG_CLEAN = 1
    MSG_PART = 2
    MSG_FULL = 3

    def __init__(self, msg_type=-1, serial=None, data=None):
        super(Message, self).__init__()
        self._state = Message.MSG_CLEAN
        self._data = None

        if not msg_type == -1:
            self._update_body(msg_type, serial, data)

    def _update_body(self, msg_type, serial, data):
        message = data + serial if data else serial

        msg_len = len(message)
        if msg_len + 3 <= 255:
            data = struct.pack(('!BB%ds' % msg_len), msg_len + 3, msg_type, message)
            data = struct.pack(('!BB%dsHBB' % len(data)), 0x78, 0x78, data, crc_encode.get_crc16(data), 13, 10)
        else:
            data = struct.pack(('!HB%ds' % msg_len), msg_len + 4, msg_type, message)
            data = struct.pack(('!BB%dsHBB' % len(data)), 0x79, 0x79, data, crc_encode.get_crc16(data), 13, 10)
        self._data = data
        self._state = Message.MSG_FULL

    def _check_message(self):
        if self._data[0] == 0x78 and self._data[1] == 0x78:
            return self._data[2] + 5 == len(self._data)
        elif self._data[0] == 0x79 and self._data[1] == 0x79:
            return self._data[2] << 8 + self._data[3] + 6 == len(self._data)
        else:
            # throw message error exception
            return False

    def parse_message(self):
        if self._data[0] == 0x78 and self._data[1] == 0x78:
            print('xxxxx', self._data[2] - 5)
            pack_struct = '!HBB%ds2sHH' % (self._data[2] - 5)
        else:
            pack_struct = '!HHB%ds2sHH' % (self._data[2] << 8 + self._data[3] - 5)
        _, length, msg_type, msg, serial, crc, stop = struct.unpack(pack_struct, self._data)
        return length, msg_type, msg, serial

    def update_data(self, data):
        self._state = Message.MSG_PART
        self._data = data
        if self._check_message():
            self._state = Message.MSG_FULL

    def append_data(self, data):
        self._data = self._data + data

        if self._check_message():
            self._state = Message.MSG_FULL

    def clean(self):
        self._data = None
        self._state = Message.MSG_CLEAN

    def get_bytes(self):
        return self._data

    def get_state(self):
        return self._state


class MessageManager(object):
    FREE_IDS = [1 if item == 0 else item + 1 for item in range(255)]

    def __init__(self):
        super(MessageManager, self).__init__()
        self._message = Message()
        self._id = self._get_free_id()

    def _get_free_id(self):
        free_id = MessageManager.FREE_IDS[0]
        MessageManager.FREE_IDS[0] = MessageManager.FREE_IDS[free_id]

        return free_id

    def add_read_data(self, data):
        if self._message.get_state() == Message.MSG_CLEAN: # 读取新消息
            self._message.update_data(data)
        elif self._message.get_state() == Message.MSG_PART: # 读取剩余部分消息
            self._message.append_data(data)
        else: # 错误
            pass

        return self._message
    
    def create_message(self, msg_type, data):
        _data = struct.pack(('!bI%ds' % len(data)), len(data) + 4, self._id, data)

        return Message(msg_type, b'\x00\x01', _data)

    def free(self):
        MessageManager.FREE_IDS[self._id] = MessageManager.FREE_IDS[0]
        MessageManager.FREE_IDS[0] = self._id

