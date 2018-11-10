#!/usr/bin/python
#coding:utf-8




import os

import json
import sqlite3
from tornado import web

conn = sqlite3.connect('server/db/test.db')
exam_conn = None

pos_map = {}

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
    score DOUBLE,
    create_time TIMESTAMP
);
CREATE INDEX exam_user_exam ON exam_user (exam_id);
CREATE INDEX exam_user_line ON exam_user (line_id);
CREATE INDEX exam_user_device ON exam_user (device_id);


INSERT INTO exam_user (exam_id, line_id, device_id, username, score, create_time) values (1, 1, '9C:2E:A1:EC:93:6F', '小A', 50.1, '2018-11-08T21:46:20.257750')
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
        global exam_conn

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

        # cursor = exam_conn.cursor()
        # cursor.execute('''
        #     INSERT INTO user_position_%d (latitude, longitude, type, create_time) values ('%s', %f, %f, %d, '%s')
        # ''' % (data.get('user_id'), data.get('latitude'), data.get('longitude'), data.get('type'), datetime.now().isoformat()))
        # cursor.close()
        # exam_conn.commit()

        global pos_map

        pos_map.update({
            data.get('user_id'):
            {'id': data.get('user_id'), 'latitude': data.get('latitude'), 'longitude': data.get('longitude')}
        })

        self.write(json.dumps({
            "stat": 1
        }))

class GetExamLine(web.RequestHandler):
    def get(self, device_id):
        print(device_id)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, device_id FROM exam_user where device_id='%s'
        ''' % device_id)
        exam_user = cursor.fetchone()
        if exam_user:
            cursor.execute('''
                SELECT id, name, latitude, longitude FROM exam_line WHERE user_id=%d
            ''' % exam_user(0))
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
        print('xxxxxxxxx')
        self.write(json.dumps({
            "stat": 1,
            "users": pos_map.values
            # "users": [
            #     {
            #         "id": 1,
            #         "name": '张三丰',
            #         "latitude": 96.12,
            #         "longtitude": 166.545,
            #         "score": -1
            #     },
            #     {
            #         "id": 2,
            #         "name": '李四书',
            #         "latitude": 96.12,
            #         "longtitude": 166.545,
            #         "score": -1
            #     }
            # ]
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

from backends import CursorManager, query_user, upload_position, query_line, query_position

class RouteConfig(web.Application):
    def route(self, url):
        def register(handler):
            self.add_handlers('.*$', [(url, handler)])
            return handler
        return register
        
app = RouteConfig(cookie_secret='Zxyo8feo0Ujlx')

@app.route(r'/')
class HomeIndex(web.RequestHandler):
    def get(self):
        self.write('Hello')
        
@app.route(r'/api/user/login/([^/]*)')
class UserLogin(web.RequestHandler):
    def get(self, device_id):
        with CursorManager() as cursor:
            users = query_user(cursor, device_id=device_id)
            if users:
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'user': users[0]
                }))
            else:
                self.write(json.dumps({
                    'state': 10,
                    'message': '用户未找到'
                }))

@app.route(r'/api/user/position')
class UserUploadPosition(web.RequestHandler):
    def post(self):
        params = json.loads(self.request.body)
        with CursorManager() as cursor:
            upload_position(cursor, params.get('user_id'), params.get('latitude'), params.get('longitude'), params.get('type'))

        self.write(json.dumps({
            'state': 1,
            'message': '成功',
        }))

@app.route(r'/api/user/line/(\d+)')
class UserGetLine(web.RequestHandler):
    def get(self, line_id):
        with CursorManager() as cursor:
            data = query_line(line_id)
            if data:
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'line': dat[0].get('')
                }))

@app.route(r'/api/manager/login')
class ManagerLogin(web.RequestHandler):
    def get(self):
        # , user_name, password

        self.write(json.dumps({
            'state': 1,
            'message': '成功'
        }))

@app.route(r'/api/manager/exam')
class ManagerGetExam(web.RequestHandler):
    def get(self):
        with CursorManager() as cursor:
            users = query_user(cursor)
            if users:
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'users': users
                }))
            else:
                self.write(json.dumps({
                    'state': 10,
                    'message': '没有数据',
                }))

@app.route(r'/api/manager/locations')
class ManagerGetLocations(web.RequestHandler):
    def get(self):
        with CursorManager() as cursor:
            locations = query_position(cursor)
            if locations:
                for location in locations:
                    update_time = location.get('pos_update_time')
                    if update_time:
                        update_time = datetime.datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        update_time = datetime.datetime(2000, 1, 1)
                    if location.get('latitude') and location.get('longitude'):
                        if (datetime.datetime.now() - update_time).total_score < 300:
                            location.update({'state': 1})
                        else:
                            location.update({'state': 2})
                    else:
                        location.update({'state': 3})

                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'locations': locations
                }))
            else:
                self.write(json.dumps({
                    'state': 10,
                    'message': '没有数据',
                }))

@app.route(r'/api/manager/track/(\d+)')
class ManagerGetUserTrack(web.RequestHandler):
    def get(self, user_id):
        # with CursorManager() as cursor:
        #     pass
        self.write(json.dumps({
            "state": 1,
            "message": '成功',
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


@app.route(r'/api/manager/user/result/(\d+)')
class ManagerGetUserResult(web.RequestHandler):
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

class AdminLogin(object):
    def get(self, user_name, password):
        pass

class AdminNewExam(web.RequestHandler):
    def get(self, exam_name):
        pass

class AdminSaveLine(web.RequestHandler):
    def post(self):
        pass

class AdminImportUsers(web.RequestHandler):
    def post(self):
        pass


# application = web.Application([
#     (r"/", MainHandler),
#     (r"/api/upload/position", UploadPosition),
#     (r"/api/exam/line/(.+)", GetExamLine),
#     (r"/api/exam/users", GetExamUsers),
#     (r"/api/exam/create/(\d+)", CreateExam),
#     (r"/api/exam/userspos/(\d+)", GetExamUsersPos),
#     (r"/api/exam/user/pos/(\d+)", GetExamUserPos),
#     (r"/api/exam/result/(\d+)", GetExamResult),
# ])
