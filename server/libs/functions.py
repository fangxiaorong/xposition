#!/usr/bin/python
#coding:utf-8

def hex_str(data):
    hex_value = ''
    for pu in data:
        hex_value = hex_value + str((pu >> 4) & 0xF) + str(pu & 0xF)
    return hex_value
