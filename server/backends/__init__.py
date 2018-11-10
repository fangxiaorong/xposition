#!/usr/bin/python
#coding:utf-8

from datetime import datetime

import sqlite3


conn = sqlite3.connect('server/db/test.db')

class CursorManager(object):
    def __init__(self, connect=None):
        global conn

        self._conn = connect or conn

    def __enter__(self):
        self._cursor = self._conn.cursor()
        return self._cursor

    def __exit__(self, type, value, trace):
        self._cursor.close()

'''
state: (1: 初始化， 2: 考试)
CREATE TABLE exam (
    id INTEGER PRIMARY KEY,
    name VARCHAR(40),
    username VARCHAR(20),
    state INTEGER,
    create_time TIMESTAMP
);
CREATE TABLE exam_user (
    id INTEGER PRIMARY KEY,
    exam_id INTEGER,
    line_id INTEGER,
    device_id VARCHAR(20),
    username VARCHAR(20),
    latitude DOUBLE,
    longitude DOUBLE,
    score DOUBLE,
    create_time TIMESTAMP,
    pos_update_time TIMESTAMP
);
CREATE INDEX exam_user_exam ON exam_user (exam_id);
CREATE INDEX exam_user_line ON exam_user (line_id);
CREATE INDEX exam_user_device ON exam_user (device_id);
'''

def dict_factory(cursor, row):  
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn.row_factory = dict_factory

def _query_object(cursor, table, fields, **kwargs):
    if kwargs:
        val = [(kv[0] + '="' + kv[1] + '"') for kv in kwargs.items()]
    else:
        val = ['1=1']

    try:
        sql_str = '''
            SELECT %s FROM %s WHERE %s
        ''' % (', '.join(fields), table, ' and '.join(val))
        cursor.execute(sql_str)
        return cursor.fetchall()
    except Exception as e:
        raise e
    return None

def create_exam(cursor, name):
    sql_str = '''
        INSERT INTO exam (name, state, create_time) values ('%s', 1, '%s');
    ''' % (name, datetime.now().isoformat())

    exam_id = None
    try:
        cursor.execute(sql_str)
        exam_id = cursor.lastrowid
        cursor.connection.commit()
    except Exception as e:
        pass
    return exam_id

def add_users(cursor, exam_id, users):
    try:
        for user in users:
            sql_str = '''
                INSERT INTO exam_user (exam_id, line_id, device_id, username, create_time) values (%d, %d, '%s', '%s', '%s')
            ''' % (exam_id, 1, user.get('device_id'), user.get('username'), datetime.now().isoformat())
            cursor.execute(sql_str)
        cursor.connection.commit()
    except Exception as e:
        raise e

def query_user(cursor, **kwargs):
    return _query_object(cursor, 'exam_user', ('id', 'exam_id', 'line_id', 'device_id', 'username', 'score', 'latitude', 'longitude', 'pos_update_time'), **kwargs)

def upload_position(cursor, user_id, latitude, longitude, type):
    try:
        sql_str = '''    
            UPDATE exam_user set latitude=%f, longitude=%f, pos_update_time='%s' WHERE id=%d
        ''' % (latitude, longitude, datetime.now().isoformat(), user_id)
        cursor.execute(sql_str)
        cursor.connection.commit()
    except Exception as e:
        raise e

def query_position(cursor, **kwargs):
    return _query_object(cursor, 'exam_user', ('id', 'device_id', 'username', 'latitude', 'longitude', 'pos_update_time', 'score'), **kwargs)

def query_line(cursor, line_id):
    return _query_object(cursor, 'exam_line', ('id', 'line_info'), id=line_id)

def test():
    with CursorManager() as cursor:
        # cursor.execute('select * from exam_user')
        # print(cursor.fetchall())
        # create_exam(cursor, 'test')
        # add_users(cursor, 2, [
        #     {"device_id": '11:22:33:44', "username": '张三'}
        # ])
        # print(dir(cursor.connection))
        # print(query_user(cursor, device_id='9C:2E:A1:EC:93:6F'))
        # upload_position(cursor, 1, 38.1, 116.99)
        print(query_exam(cursor))

