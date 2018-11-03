#!/usr/bin/python
#coding:utf-8

import struct

from tcpserver.message import Message
from libs.functions import hex_str

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

        return Message(LoginHandler.MSG_TYPE, serial)

class GPSInfoHandler(object):
    MSG_TYPE = 0x10
    def __init__(self):
        super(GPSInfoHandler, self).__init__()
    
    def handler(self, device, message, serial):
        year, month, day, hour, minute, second, gps_info, longtitude, latitude, speed, gps_state = struct.unpack('!BBBBBBBLLBH', message)
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)
        longtitude = longtitude / 30000
        longtitude = '%dº%f‘' % (longtitude // 60, longtitude % 60)
        latitude = latitude / 30000
        latitude = '%dº%f‘' % (longtitude // 60, longtitude % 60)

        device.longtitude = longtitude
        device.latitude = latitude
        device.speed = speed

        print('receive gps', date_time, longtitude, latitude, speed)

class HeartHandler(object):
    MSG_TYPE = 0x13
    def __init__(self):
        super(HeartHandler, self).__init__()
    
    def handler(self, device, message, serial):
        device_info, battery, signal = struct.unpack('!BBB', message[:3])
        heart_type = (device_info >> 2) & 0xF

        device.battery = battery
        device.signal = signal

        print('receive heart', heart_type, battery, signal)

        return Message(HeartHandler.MSG_TYPE, serial)

class TimeSyncHandler(object):
    MSG_TYPE = 0x1F
    def __init__(self):
        super(TimeSyncHandler, self).__init__()
    
    def handler(self, device, message, serial):
        year, month, day, hour, minute, second = struct.unpack('!BBBBBB', message[:6])
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)

        print('receive settime', date_time)

        data = struct.pack('!LH', int(datetime.datetime.utcnow().timestamp()), 0)
        return Message(TimeSyncHandler.MSG_TYPE, serial, data)

