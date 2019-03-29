#!/usr/bin/python
#coding:utf-8

class DeviceInfo(object):
    EVENT_INIT = 1
    EVENT_POSITION = 2
    EVENT_CHECKIN = 3

    def __init__(self):
        super(DeviceInfo, self).__init__()
        self.imei = None
        self.latitude = None
        self.longitude = None
