#!/usr/bin/python
#coding:utf-8

from queue import Queue

from tornado.tcpserver import TCPServer

from tcpserver.message import Message
from tcpserver.device import Device

class Connection(object):
    clients = set()
    def __init__(self, stream, address):
        super(Connection, self).__init__()
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        print("A new user has entered the chat room.", self._address)

    def on_close(self):
        print("A user has left the chat room.", self._address)
        Connection.clients.remove(self)
        

class RobotConnection(object):
    _callback_map = {}

    def __init__(self, stream, address):
        super(RobotConnection, self).__init__(stream, address)
        self._send_array = Queue()
        self._sending_message = None
        self._message = Message()
        self._device = Device()
        self._connect_loop()

    def _connect_loop(self):
        if self._message.get_state() == Message.MSG_PART: # 读取完整消息
            self._read_data()
        elif self._message.get_state() == Message.MSG_FULL: # 完整消息处理
            if self._sending_message:
                self._sending_handler(self._message, self._sending_message)
                self._sending_message = None
            else:
                self._message_handler(self._message)
            # 处理完消息后，重置消息
            self._message.clean()
        elif self._message.get_state() == Message.MSG_CLEAN and not self._send_array.empty():  # 发送消息
            self._sending_message = self._send_array.get()
            self._stream.write(self._sending_message.get_bytes())
        else: # 监听
            self._read_data()

        # 事件处理循环
        self._connect_loop()

    def _read_data(self):
        self._stream.read_until('\r\n', self._read_callback, 1024)

    def _read_callback(self, data):
        if self._message.get_state() == Message.MSG_CLEAN: # 读取新消息
            self._message.update_data(data)
        elif self._message.get_state() == Message.MSG_PART: # 读取剩余部分消息
            self._message.append_data(data)
        else:
            pass # exception

    def _sending_handler(self, message):
        pass

    def _message_handler(self, message):
        length, msg_type, msg, serial = message.parse_message()
        callback = RobotConnection._callback_map.get(msg_type)
        if callback:
            send_msg = callback.handler(self._device, msg, serial)
            if send_msg:
                self._stream.write(send_msg.get_bytes())
        else:
            print(msg_type, 'message handler is not set.')

    def send_message(self, message):
        self._send_array.put(message)


class GPSServer(TCPServer):
    def handle_stream(self, stream, address):
        print("New connection :", address, stream)
        RobotConnection(stream, address) 
        print("connection num is:", len(Connection.clients))

    def set_message_handler(self, callback):
        RobotConnection._callback_map.update({callback.MSG_TYPE: callback()})

