#!/usr/bin/python
#coding:utf-8

from libs import crc_encode



class Message(object):
    MSG_CLEAN = 1
    MSG_PART = 2
    MSG_FULL = 3

    def __init__(self):
        super(Message, self).__init__()
        self._state = Message.MSG_CLEAN

    def _decode(self, data):
        pass

    def update_body(self, data, serial):
        pass

    def get_data(self):
        pass

    def get_state(self):
        return self._state
