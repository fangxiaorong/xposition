#!/usr/bin/python
#coding:utf-8

from libs import crc_encode



class Message(object):
    MSG_CLEAN = 1
    MSG_PART = 2
    MSG_FULL = 3

    def __init__(self, serial=None, data=None):
        super(Message, self).__init__()
        self._state = Message.MSG_CLEAN
        self._data = None

        if serial:
            self._update_body(serial, data)

    def _update_body(self, serial, data):
        message = data + serial if data else serial

        msg_len = len(message)
        if msg_len + 3 <= 255:
            data = struct.pack(('!BB%ds' % msg_len), msg_len + 3, msg_type, message)
            data = struct.pack(('!BB%dsHBB' % len(data)), 0x78, 0x78, data, get_crc16(data), 13, 10)
        else:
            data = struct.pack(('!HB%ds' % msg_len), msg_len + 4, msg_type, message)
            data = struct.pack(('!BB%dsHBB' % len(data)), 0x79, 0x79, data, get_crc16(data), 13, 10)
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
            pack_struct = '!HBB%ds2sHH' % self._data[2] - 5
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
