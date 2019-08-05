#!/usr/bin/python
#coding:utf-8

from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop

# from tcpserver.message import Message, MessageManager
# from tcpserver.device import DeviceInfo

# from backends import add_device_record

class MessageHandler(object):
    def __init__(self):
        super(MessageHandler, self).__init__()

class LoginHandler(MessageHandler):
    MSG_TYPE = 0x01
    def __init__(self):
        super(LoginHandler, self).__init__()

    def handler(self, device, message, serial):
        imei, device_no = struct.unpack('!8sH', message[:10])
        imei = hex_str(imei)

        device.imei = imei
        device.device_no = device_no

        print('receive login', imei, device_no)

        return Message(LoginHandler.MSG_TYPE, serial), device.EVENT_INIT


class Message(object):
    MSG_PART = 2
    MSG_FULL = 3
    def __init__(self):
        super(Message, self).__init__()
        self._state = Message.MSG_PART
        self._data = None

    def get_need_bytes(self):
        pass

    def add_data(self, data):
        if self._data == None:
            self._data = data
        else:
            self._data += data

        need_bytes = self.get_need_bytes()
        if need_bytes == 0:
            self._state = Message.MSG_FULL
            need_bytes = self.get_need_bytes()
        return need_bytes

    def get_state(self):
        return self._state

    def clean(self):
        self._data = None
        self._state = Message.MSG_PART

class Reader(object):
    def __init__(self, stream, message, callback):
        super(Reader, self).__init__()
        self.stream = stream
        self.message = message
        self.callback = callback

    def _read_loop(self, data):
        size = self.message.add_data(data)
        if self.message.get_state() == Message.MSG_FULL:
            self.callback(self.message)
            self.message.clean()
        self.read_data(size)

    def read_data(self, size):
        pass

class LinkMessage(Message):
    def get_need_bytes(self):
        if self._data is None or self.get_state() == Message.MSG_FULL:
            return 7
        return (self._data[3] << 4 + self._data[4] + 3) - len(self._data)

class LinkReader(Reader):
    def read_data(size):
        self.stream.read_bytes(size, self._read_loop)

class Connection(object):
    clients = set()
    def __init__(self, stream, address):
        super(Connection, self).__init__()
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
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
        self.reader = LinkReader(stream, LinkMessage(), self._message_handler)

    def _write_loop(self):
        if len(self._send_array) > 0:
            msg = self._send_array.pop(0)
            self._send_message(msg)
            print('send:::', msg.get_bytes())

        IOLoop.current().call_later(5, self._write_loop)

    def _event_resolver(self, event):
        if event == self._device.EVENT_INIT:
            self._send_array.append(self.create_message(0x80, b'GPSON#'))
            self._send_array.append(self.create_message(0x80, b'TIME|1|1|\x01\x00\x17\x00|||||||]\x01\x00\x17\x00|||||||]\x01\x00\x17\x00|||||||}'))

            add_device_record(self._device.imei)
        elif event == self._device.EVENT_POSITION:
            add_device_record(self._device.imei, self._device.latitude, self._device.longitude)
        elif event == self._device.EVENT_CHECKIN:
            add_device_record(self._device.imei, self._device.latitude, self._device.longitude, True)

    def _send_message(self, message):
        if self._stream:
            self._stream.write(message.get_bytes())

    def _message_handler(self, message):
        length, msg_type, msg, serial = message.parse_message()
        callback = RobotConnection._callback_map.get(msg_type)
        if callback:
            send_msg, event = callback.handler(self._device, msg, serial)
            if send_msg:
                self._send_message(send_msg)
            if event:
                self._event_resolver(event)
        else:
            print(msg_type, 'message handler is not set.')

class GPSServer(TCPServer):
    def __init__(self):
        super(GPSServer, self).__init__()

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
 
