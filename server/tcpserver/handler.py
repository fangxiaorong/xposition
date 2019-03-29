#!/usr/bin/python
#coding:utf-8

import struct
import datetime

from tcpserver.message import Message
from libs.functions import hex_str

from backends import ExamCalculate

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

class GPSInfoHandler(object):
    MSG_TYPE = 0x10
    def __init__(self):
        super(GPSInfoHandler, self).__init__()
    
    def handler(self, device, message, serial):
        year, month, day, hour, minute, second, gps_info, latitude, longitude, speed, gps_state, extend = struct.unpack('!BBBBBBBLLBHH', message)
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)
        longitude = longitude / 30000 / 60
        latitude = latitude / 30000 / 60

        latitude, longitude = ExamCalculate.gps_to_amap(latitude, longitude)

        device.longitude = longitude
        device.latitude = latitude
        device.speed = speed

        print('receive gps', date_time, longitude, latitude, speed)

        return None, device.EVENT_POSITION

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

        return Message(HeartHandler.MSG_TYPE, serial), None

class TimeSyncHandler(object):
    MSG_TYPE = 0x1F
    def __init__(self):
        super(TimeSyncHandler, self).__init__()
    
    def handler(self, device, message, serial):
        year, month, day, hour, minute, second = struct.unpack('!BBBBBB', message[:6])
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)

        print('receive settime', date_time)

        data = struct.pack('!LH', int(datetime.datetime.utcnow().timestamp()), 0)
        return Message(TimeSyncHandler.MSG_TYPE, serial, data), None


class CheckInOutHandler(object):
    MSG_TYPE = 0xB0
    def __init__(self):
        super(CheckInOutHandler, self).__init__()
    
    def handler(self, device, message, serial):
        year, month, day, hour, minute, second, gps_fix, reserve, gps_num, latitude, longitude, speed = struct.unpack('!BBBBBBBHBLLB', message[:19])
        date_time = '%d-%d-%d %d:%d:%d' % (year + 2000, month, day, hour, minute, second)

        longitude = longitude / 30000 / 60
        latitude = latitude / 30000 / 60

        latitude, longitude = ExamCalculate.gps_to_amap(latitude, longitude)

        print('check time', date_time)
        print('reserve', reserve)
        print('gps:', gps_num, latitude, longitude, speed)

        device.longitude = longitude
        device.latitude = latitude
        device.speed = speed

        date = datetime.datetime.now()
        data = struct.pack('!BBBBBBBBH', date.year - 2000, date.month, date.day, date.hour, date.minute, date.second, 1, 1, reserve)
        return Message(CheckInOutHandler.MSG_TYPE, serial, data), device.EVENT_CHECKIN


class UpCtrlHandler(object):
    MSG_TYPE = 0x81
    def __init__(self):
        super(UpCtrlHandler, self).__init__()
    
    def _set_fn_handler(self):
        pass

    def _set_sos_handler(self):
        pass

    def _set_gps_handler(self):
        pass

    def handler(self, device, message, serial):
        pass
