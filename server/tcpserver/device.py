#!/usr/bin/python
#coding:utf-8

class DeviceInfo(object):
	EVENT_INIT = 1

	def __init__(self):
		super(DeviceInfo, self).__init__()
		self.events = []
