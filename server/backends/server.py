#!/usr/bin/python
#coding:utf-8




import os
from datetime import datetime
import json
import sqlite3
from tornado import web

conn = sqlite3.connect('server/db/test.db')
exam_conn = None

'''
type: (1: 上传, 2: 自动)
CREATE TABLE user_position (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    device_id VARCHAR(20),
    latitude DOUBLE,
    longitude DOUBLE,
    type INTEGER,
    create_time TIMESTAMP
);
CREATE INDEX user_position_user ON user_position (user_id);
CREATE INDEX user_position_device ON user_position (device_id);
CREATE TABLE exam_line (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20),
    latitude DOUBLE,
    longitude DOUBLE,
    starttime TIMESTAMP,
    endtime TIMESTAMP,
    order_index INTEGER,
    valid INTEGER,
    weight DOUBLE,
    create_time TIMESTAMP
);
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
    create_time TIMESTAMP
);
CREATE INDEX exam_user_exam ON exam_user (exam_id);
CREATE INDEX exam_user_line ON exam_user (line_id);
CREATE INDEX exam_user_device ON exam_user (device_id);


INSERT INTO exam_user (exam_id, line_id, device_id, username, create_time) values (1, 1, '9C:2E:A1:EC:93:6F', '小A', '2018-11-08T21:46:20.257750')
'''
class NewExam(web.RequestHandler):
    def get(self, exam_id):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exam (name, username, state, create_time) values ('%s', '%s', 1, '%s')
        ''' % ('2018-10-10-123', 'xyz', datetime.now().isoformat()))
        cursor.close()
        conn.commit()
        

class CreateExam(web.RequestHandler):
    def get(self, exam_id):
        exam_id = int(exam_id)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT state, name FROM exam WHERE id=%d
        ''' % exam_id)
        state, name = cursor.fetchone()
        if state == 1:
            cursor.execute('''
            UPDATE exam set state=2 WHERE id=%d
        ''' % exam_id)

        if not os.path.exists('server/db/' + name + '.db'):
            _conn = sqlite3.connect('server/db/' + name + '.db')
            _cursor = _conn.cursor()
            cursor.execute('''
                SELECT id, line_id, username FROM exam_user WHERE exam_id=%d
            ''' % exam_id)
            for data in cursor:
                print(data)
                _cursor = _conn.execute('''
                    CREATE TABLE user_position_%d (
                        id INTEGER PRIMARY KEY,
                        latitude DOUBLE,
                        longitude DOUBLE,
                        type INTEGER,
                        create_time TIMESTAMP
                    );
                ''' % data[0])
            _cursor.close()
            _conn.commit()
            exam_conn = _conn
        else:
            exam_conn = sqlite3.connect('server/db/' + name + '.db')

        self.write(json.dumps({
            "stat": 1,
            "message": '成功'
        }))
        


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class UploadPosition(web.RequestHandler):
    def post(self):
        print(self.request.body)
        data = json.loads(self.request.body)

        cursor = exam_conn.cursor()
        cursor.execute('''
            INSERT INTO user_position_%d (latitude, longitude, create_time) values ('%s', %f, %f, '%s')
        ''' % (data.get('user_id'), data.get('latitude'), data.get('longitude'), datetime.now().isoformat()))
        cursor.close()
        exam_conn.commit()
        self.write(json.dumps({
            "stat": 1
        }))

class GetExamLine(web.RequestHandler):
    def get(self, mac):
        print(mac)
        cursor = conn.cursor()
        cursor.execute('''
        ''')
        self.write(json.dumps({
            "stat": 1,
            "message": '成功',
            "userid": 1,
            "username": '张三丰',
            "linename": "测试路线1",
            "positions": [
                {
                    "id": 123456,
                    "name": 'xyz',
                    "latitude": 39.98620582307232,
                    "longitude": 116.31460294485826,
                },
                {
                    "id": 123456,
                    "name": 'xyz',
                    "latitude": 39.96,
                    "longitude": 116.35460294485826,
                }
            ]
        }))

class GetExamUsers(web.RequestHandler):
    def get(self):
        self.write(json.dumps({
            "stat": 1,
            "users": [
                {
                    "id": 1,
                    "name": '张三丰',
                    "latitude": 96.12,
                    "longtitude": 166.545,
                    "score": -1
                },
                {
                    "id": 2,
                    "name": '李四书',
                    "latitude": 96.12,
                    "longtitude": 166.545,
                    "score": -1
                }
            ]
        }))

class GetExamList(web.RequestHandler):
    def get(self):
        self.write(json.dumps({
            "stat": 1,
            "users": [
                {
                    "id": 123456,
                    "name": 'xyz',
                    "score": 100,
                }
            ]
        }))

class getExamUserDetail(web.RequestHandler):
    def get(self):
        self.write(json.dumps({
            "stat": 1,
            "linename": "xxx",
            "positions": [
                {
                    "id": 1,
                    "latitude": 96.12,
                    "longtitude": 166.545,
                    "score": 1
                }
            ]
        }))
                        
class GetExamUsersPos(web.RequestHandler):
    def get(self, exam_id):
        self.write(json.dumps({
            "stat": 1,
            "linename": "xxx",
            "users": [
                {
                    "id": 1,
                    "latitude": 39.78620582307232,
                    "longitude": 116.31460294485826,
                    "score": 1
                },
                {
                    "id": 2,
                    "latitude": 39.88620582307232,
                    "longitude": 116.31460294485826,
                    "score": 1
                }
            ]
        }))

class GetExamUserPos(web.RequestHandler):
    def get(self, exam_id):
        self.write(json.dumps({
            "stat": 1,
            "points": [
                { "latitude": 39.78620582307232, "longitude": 116.31460294485826, },
                { "latitude": 39.77620582307232, "longitude": 116.32460294485826, },
                { "latitude": 39.76620582307232, "longitude": 116.32460294485826, },
                { "latitude": 39.76620582307232, "longitude": 116.32460294485826, },
                { "latitude": 39.75620582307232, "longitude": 116.33460294485826, },
                { "latitude": 39.75620582307232, "longitude": 116.33460294485826, },
                { "latitude": 39.74620582307232, "longitude": 116.33460294485826, },
                { "latitude": 39.74620582307232, "longitude": 116.33460294485826, },
                { "latitude": 39.74620582307232, "longitude": 116.33460294485826, },
                { "latitude": 39.73620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.74620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.73620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.73620582307232, "longitude": 116.35460294485826, },
                { "latitude": 39.73620582307232, "longitude": 116.35460294485826, },
                { "latitude": 39.74620582307232, "longitude": 116.35460294485826, },
                { "latitude": 39.73620582307232, "longitude": 116.35460294485826, },
                { "latitude": 39.72620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.72620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.72620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.71620582307232, "longitude": 116.34460294485826, },
                { "latitude": 39.71620582307232, "longitude": 116.34460294485826, },
            ]
        }))

class GetExamResult(web.RequestHandler):
    def get(self, user_id):
        self.write(json.dumps({
            "stat": 1,
            "linename": "xxx",
            "total_score": 88.8,
            "points": [
                {
                    "id": 1,
                    "latitude": 39.78620582307232,
                    "longitude": 116.31460294485826,
                    "weight": 0.3,
                    "score": 1
                },
                {
                    "id": 2,
                    "latitude": 39.88620582307232,
                    "longitude": 116.31460294485826,
                    "weight": 0.5,
                    "score": 1
                },
                {
                    "id": 3,
                    "latitude": 39.88620582307232,
                    "longitude": 116.31460294485826,
                    "weight": 0.2,
                    "score": 1
                }
            ]
        }))

application = web.Application([
    (r"/", MainHandler),
    (r"/api/upload/position", UploadPosition),
    (r"/api/exam/line/(.+)", GetExamLine),
    (r"/api/exam/users", GetExamUsers),
    (r"/api/exam/create/(\d+)", CreateExam),
    (r"/api/exam/userspos/(\d+)", GetExamUsersPos),
    (r"/api/exam/user/pos/(\d+)", GetExamUserPos),
    (r"/api/exam/result/(\d+)", GetExamResult),
])
