#!/usr/bin/python
#coding:utf-8

from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop

from tcpserver.message import Message, MessageManager
from tcpserver.device import DeviceInfo

class Connection(object):
    clients = set()
    def __init__(self, stream, address):
        super(Connection, self).__init__()
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._message = MessageManager()
        self._stream.set_close_callback(self.on_close)
        print("A new user has entered the chat room.", self._address)

    def resolve_data(self, data):
        return self._message.add_read_data(data)

    def create_message(self, msg_type, data):
        return self._message.create_message(msg_type, data)

    def on_close(self):
        print("A user has left the chat room.", self._address)
        self._stream = None
        self._message.free()
        Connection.clients.remove(self)

class RobotConnection(Connection):
    _callback_map = {}

    def __init__(self, stream, address):
        super(RobotConnection, self).__init__(stream, address)
        self._send_array = []
        self._device = DeviceInfo()
        self._handler()

    def _read_loop(self, data):
        print(data)
        message = self.resolve_data(data)
        
        if message.get_state() == Message.MSG_FULL: # 完整消息处理
             self._message_handler(message)
             message.clean()

        if self._stream:
            self._stream.read_until(b'\r\n', self._read_loop, 1024)

    def _write_loop(self):
        if len(self._send_array) > 0:
            msg = self._send_array.pop(0)
            self._send_message(msg)
            print('send:::', msg.get_bytes())

        IOLoop.current().call_later(5, self._write_loop)

    def _event_resolver(self):
        while len(self._device.events) > 0:
            event = self._device.events.pop(0)
            if event == self._device.EVENT_INIT:
                self._send_array.append(self.create_message(0x80, b'GPSON#'))
                self._send_array.append(self.create_message(0x80, b'TIME|1|1|\x0B\x00\x14\x00|||||||]\x0B\x00\x14\x00|||||||]\x0B\x00\x14\x00|||||||}'))

    def _send_message(self, message):
        if self._stream:
            self._stream.write(message.get_bytes())

    def _handler(self):
        self._stream.read_until(b'\r\n', self._read_loop, 1024)
        self._write_loop()

    def _message_handler(self, message):
        length, msg_type, msg, serial = message.parse_message()
        callback = RobotConnection._callback_map.get(msg_type)
        if callback:
            send_msg = callback.handler(self._device, msg, serial)
            if send_msg:
                self._send_message(send_msg)
            self._event_resolver()
        else:
            print(msg_type, 'message handler is not set.')


class GPSServer(TCPServer):
    def __init__(self):
        super(GPSServer, self).__init__()

        from tcpserver import handler
        GPSServer.register_handler([
            handler.LoginHandler,
            handler.GPSInfoHandler,
            handler.HeartHandler,
            handler.TimeSyncHandler,
            handler.CheckInOutHandler,
        ])

    def handle_stream(self, stream, address):
        print("New connection :", address, stream)
        RobotConnection(stream, address) 
        print("connection num is:", len(Connection.clients))

    @staticmethod
    def register_handler(handers):
        for hander in handers:
            RobotConnection._callback_map.update({hander.MSG_TYPE: hander()})
 

