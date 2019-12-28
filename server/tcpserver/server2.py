#!/usr/bin/python
#coding:utf-8

import time
import struct
from datetime import datetime
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop

from libs.functions import hex_str
from tcpserver.device import DeviceInfo

from backends import add_device_record
from backends import ExamCalculate

def logger(device, handler, *args):
    print(datetime.now().isoformat(), '[' + device.imei + ']', handler.__class__.__name__, *args)

class MessageHandler(object):
    def __init__(self):
        super(MessageHandler, self).__init__()

    def utc2local(self, utc_st):
        now_stamp = time.time()
        local_time = datetime.fromtimestamp(now_stamp)
        utc_time = datetime.utcfromtimestamp(now_stamp)
        offset = local_time - utc_time
        local_st = utc_st + offset
        return local_st

    def position_decode(self, message):
        index = 0
        gps_time, mask = struct.unpack('!LB', message[index: index + 5])
        index += 5

        gps_time = self.utc2local(datetime.fromtimestamp(gps_time))

        latitude, longitude, altitude, speed, course, satellites = None, None, None, None, None, None
        if mask & 0x1:  # gps
            latitude, longitude, altitude, speed, course, satellites = struct.unpack('!llhHHB', message[index: index + 15])
            index += 15

            longitude = longitude / 30000 / 60
            latitude = latitude / 30000 / 60
            latitude, longitude = ExamCalculate.gps_to_amap(latitude, longitude)

        if mask & 0x2:  # BSID0
            index += 11

        if mask & 0x4:  # BSID1
            index += 7

        if mask & 0x8:  # BSID2
            index += 7

        if mask & 0x10:  # BSS0
            index += 7

        if mask & 0x20:  # BSS1
            index += 7

        if mask & 0x40:  # BSS2
            index += 7

        return index, gps_time, latitude, longitude, altitude, speed, course, satellites

    def handler(self, device, message, serial):
        pass


class LoginHandler(MessageHandler):
    MSG_TYPE = 0x01

    def __init__(self):
        super(LoginHandler, self).__init__()

    def handler(self, device, message, serial):
        imei, language = struct.unpack('!8sB', message)
        _imei = hex_str(imei)

        device.imei = _imei

        # print('receive login:', _imei, language)
        logger(device, self, language)

        data = struct.pack('!L', int(datetime.utcnow().timestamp()))
        return LinkMessage(LoginHandler.MSG_TYPE, serial, data), device.EVENT_INIT


class GPSInfoHandler(MessageHandler):
    MSG_TYPE = 0x02

    def handler(self, device, message, serial):
        gps_time, latitude, longitude, speed, direction, base, state = struct.unpack('!LLLBH9sB', message)

        gps_time = self.utc2local(datetime.fromtimestamp(gps_time))
        longitude = longitude / 30000 / 60
        latitude = latitude / 30000 / 60

        latitude, longitude = ExamCalculate.gps_to_amap(latitude, longitude)

        # print('receive gps:', time, longitude, latitude, speed, direction)
        logger(device, self, time, longitude, latitude, speed, direction)

        return None, None


class HeartHandler(MessageHandler):
    MSG_TYPE = 0x03

    def handler(self, device, message, serial):
        # print('receive heart:', message)
        logger(device, self, message)

        return LinkMessage(HeartHandler.MSG_TYPE, serial), None


class NormalHandler(MessageHandler):
    MSG_TYPE = 0x12

    def handler(self, device, message, serial):
        index, gps_time, latitude, longitude, altitude, speed, course, satellites = self.position_decode(message)

        # print('receive normal:', gps_time, longitude, latitude, altitude, speed, course, satellites)
        logger(device, self, gps_time, longitude, latitude, altitude, speed, course, satellites)

        if longitude is not None and latitude is not None:
            device.longitude = longitude
            device.latitude = latitude
            device.speed = speed

            return LinkMessage(NormalHandler.MSG_TYPE, serial), device.EVENT_POSITION

        return LinkMessage(NormalHandler.MSG_TYPE, serial), None


class WarringHandler(MessageHandler):
    MSG_TYPE = 0x14

    def handler(self, device, message, serial):
        index, gps_time, latitude, longitude, altitude, speed, course, satellites = self.position_decode(message)

        w_type, status = struct.unpack('!BH', message[index:])

        # print('recevie warring:', gps_time, longitude, latitude, altitude, speed, course, satellites, w_type, status)
        logger(device, self, gps_time, longitude, latitude, altitude, speed, course, satellites, w_type, status)

        if longitude is not None and latitude is not None:
            device.longitude = longitude
            device.latitude = latitude
            device.speed = speed
            return LinkMessage(WarringHandler.MSG_TYPE, serial), device.EVENT_CHECKIN

        return LinkMessage(WarringHandler.MSG_TYPE, serial), None

class Message(object):
    MSG_PART = 2
    MSG_FULL = 3

    def __init__(self, msg_type=None, serial=None, data=None):
        super(Message, self).__init__()
        if msg_type is None:
            self._state = Message.MSG_PART
            self._data = None
        else:
            self.encode_message(msg_type, serial, data)

    def get_need_bytes(self):
        pass

    def add_data(self, data):
        if self._data is None:
            self._data = data
        else:
            self._data += data

        need_bytes = self.get_need_bytes()
        if need_bytes == 0:
            self._state = Message.MSG_FULL
            need_bytes = self.get_need_bytes()
        return need_bytes

    def decode_message(self):
        pass

    def encode_message(self, msg_type, serial, data):
        pass

    def get_state(self):
        return self._state

    def get_data(self):
        return self._data

    def clean(self):
        self._data = None
        self._state = Message.MSG_PART


class Reader(object):
    def __init__(self, stream, message, callback):
        super(Reader, self).__init__()
        self.stream = stream
        self.message = message
        self.callback = callback
        self._read_loop(None)

    def _read_loop(self, data):
        size = self.message.add_data(data)
        # print(data, size)
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
        return (self._data[3] << 4) + self._data[4] + 5 - len(self._data)

    def encode_message(self, msg_type, serial, data):
        self._state = Message.MSG_FULL
        if data is None:
            self._data = struct.pack('!BBBHH', 0x67, 0x67, msg_type, 2, serial)
        else:
            self._data = struct.pack(('!BBBHH%ds' % len(data)), 0x67, 0x67, msg_type, len(data) + 2, serial, data)

    def decode_message(self):
        head1, head2, msg_type, msg_len, serial = struct.unpack('!BBBHH', self._data[:7])
        if head1 == 0x67 and head2 == 0x67:
            print('new message....')
        return msg_len, msg_type, self._data[7:], serial


class LinkReader(Reader):
    def read_data(self, size):
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
            # print('send:::', msg.get_bytes())
            logger(self._device, self, 'SEND', msg.get_bytes())

        IOLoop.current().call_later(5, self._write_loop)

    def _event_resolver(self, event):
        if event == self._device.EVENT_INIT:
            add_device_record(self._device.imei)
        elif event == self._device.EVENT_POSITION:
            add_device_record(self._device.imei, self._device.latitude, self._device.longitude)
        elif event == self._device.EVENT_CHECKIN:
            add_device_record(self._device.imei, self._device.latitude, self._device.longitude, True)

    def _send_message(self, message):
        if self._stream:
            # print('send message:', message.get_data())
            self._stream.write(message.get_data())

    def _message_handler(self, message):
        msg_len, msg_type, content, serial = message.decode_message()
        callback = RobotConnection._callback_map.get(msg_type)
        if callback:
            send_msg, event = callback.handler(self._device, content, serial)
            if send_msg:
                self._send_message(send_msg)
            if event:
                self._event_resolver(event)
        else:
            # print(msg_type, 'message handler is not set.')
            logger(self._device, self, 'UNKNOW MESSAGE', msg_type, content)


class GPSServer(TCPServer):
    def __init__(self):
        super(GPSServer, self).__init__()

        GPSServer.register_handler([
            LoginHandler,
            GPSInfoHandler,
            HeartHandler,
            NormalHandler,
            WarringHandler,
        ])
        LinkMessage()

    def handle_stream(self, stream, address):
        print("New connection :", address, stream)
        RobotConnection(stream, address) 
        print("connection num is:", len(Connection.clients))

    @staticmethod
    def register_handler(handlers):
        for handler in handlers:
            RobotConnection._callback_map.update({handler.MSG_TYPE: handler()})
 
