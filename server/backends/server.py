#!/usr/bin/python
#coding:utf-8




import os
from datetime import datetime

import json
import sqlite3
from tornado import web
import functools

conn = sqlite3.connect('server/db/test.db')
exam_conn = None

pos_map = {}


class BaseHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/x-www-form-urlencoded')

# from backends import init_db, CursorManager, query_user, upload_position, query_line, query_position, Session
from backends import *

class RouteConfig(web.Application):
    def route(self, url):
        def register(handler):
            self.add_handlers('.*$', [(url, handler)])
            return handler
        return register
        
app = RouteConfig(cookie_secret='Zxyo8feo0Ujlx', xsrf_cookies=False, debug=True)
session = Session()

def auth_check(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        session_id = self.get_secure_cookie("session_id")
        self.user_info = session.get_user_info(session_id.decode('utf-8')) if session_id else None
        if self.user_info:
            return method(self, *args, **kwargs)
        else:
            self.write(json.dumps({
                'state': 2,
                'message': '用户未登陆',
            }))
    return wrapper

@app.route(r'/')
class HomeIndex(web.RequestHandler):
    def get(self):
        self.write('Hello')

# 用户端接口

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

# 管理端App接口

@app.route(r'/api/manager/login')
class ManagerLogin(web.RequestHandler):
    @auth_check
    def get(self):
        if self.user_info:
            self.write(json.dumps({
                'user_info': self.user_info,
                'state': 1,
                'message': '成功',
            }))
        else:
            self.write(json.dumps({
                'state': 2,
                'message': '用户未登陆',
            }))

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        state = 1
        message = '成功'
        user_info = None
        if username and password:
            with CursorManager() as cursor:
                user_info = query_user(cursor, username, password)
                if user_info:
                    if user_info.pop('password') == password:
                        self.set_secure_cookie("session_id", session.get_session_id(user_info))
                    else:
                        user_info = None
                        state = 2
                        message = '密码错误'
                else:
                    state = 3
                    message = '用户未找到'

        self.write(json.dumps({
            'state': state,
            'message': message,
            'user_info': user_info
        }))

@app.route(r'/api/manager/exam')
class ManagerGetExam(BaseHandler):
    @auth_check
    def get(self):
        with CursorManager() as cursor:
            users = query_user(cursor)
            if users:
                for location in users:
                    update_time = location.get('pos_update_time')
                    if update_time:
                        update_time = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        update_time = datetime(2000, 1, 1)
                    if location.get('latitude') and location.get('longitude'):
                        if (datetime.now() - update_time).total_seconds() < 300:
                            location.update({'state': 1})
                        else:
                            location.update({'state': 2})
                    else:
                        location.update({'state': 3})

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
                        update_time = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        update_time = datetime(2000, 1, 1)
                    if location.get('latitude') and location.get('longitude'):
                        if (datetime.now() - update_time).total_seconds() < 300:
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

# Web后台管理接口

@app.route(r'/api/admin/login')
class AdminLogin(BaseHandler):
    @auth_check
    def get(self):
        self.write(json.dumps({
            'user_info': self.user_info,
            'state': 1,
            'message': '成功',
        }))

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        state = 1
        message = '成功'
        user_info = None
        if username and password:
            with CursorManager() as cursor:
                user = table_manager(User)
                user_info = user.query_record(cursor, username=username)
                if user_info:
                    if user_info.pop('password') == password:
                        self.set_secure_cookie("session_id", session.get_session_id(user_info))
                    else:
                        user_info = None
                        state = 2
                        message = '密码错误'
                else:
                    state = 3
                    message = '用户未找到'

        self.write(json.dumps({
            'state': state,
            'message': message,
            'user_info': user_info
        }))

@app.route(r'/api/admin/user/add')
class AdminAddUser(BaseHandler):
    @auth_check
    def post(self):
        nickname = self.get_argument('nickname') #.decode('utf-8')
        password = self.get_argument('password') #.decode('utf-8')
        username = self.get_argument('username') #.decode('utf-8')

        with CursorManager() as cursor:
            user = table_manager(User)
            user_info = user.query_record(cursor, username=username)
            if user_info:
                self.write(json.dumps({
                    'state': 2,
                    'message': '用户已存在'
                }))
            else:
                if user.new_record(cursor, username, nickname, password):
                    self.write(json.dumps({
                        'state': 1,
                        'message': '成功'
                    }))
                else:
                    self.write(json.dumps({
                        'state': 3,
                        'message': '用户创建失败'
                    }))

@app.route(r'/api/admin/user/list')
class AdminUserList(BaseHandler):
    @auth_check
    def get(self):
        with CursorManager() as cursor:
            user = table_manager(User)
            user_infos = user.query_records(cursor)

            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'users': user_infos
            }))

@app.route(r'/api/admin/exam')
class AdminNewExam(BaseHandler):
    @auth_check
    def post(self):
        exam_name = self.get_argument('name')

        with CursorManager() as cursor:
            exam = table_manager(Exam)
            exam_id = exam.new_record(cursor, exam_name)
            if exam_id:
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'exam_id': exam_id,
                }))
            else:
                self.write(json.dumps({
                    'state': 2,
                    'message': '失败',
                }))

@app.route(r'/api/admin/exams')
class AdminGetExams(BaseHandler):
    @auth_check
    def get(self):
        with CursorManager() as cursor:
            exam = table_manager(Exam)
            exam_infos = exam.query_records(cursor)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'exams': exam_infos,
            }))

@app.route(r'/api/admin/exam/(\d+)')
class AdminGetExam(BaseHandler):
    def get(self, exam_id):
        with CursorManager() as cursor:
            exam = quer_exam(cursor, id=exam_id)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'exam': exam,
            }))

@app.route(r'/api/admin/examuser/list/(\d+)')
class AdminGetExamUsers(BaseHandler):
    @auth_check
    def get(self, exam_id):
        with CursorManager() as cursor:
            exam_user = table_manager(ExamUser)
            exam_user_infos = exam_user.query_records(cursor, exam_id=exam_id)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'users': exam_user_infos,
            }));

@app.route(r'/api/admin/examline/list')
class AdminGetExamLines(BaseHandler):
    @auth_check
    def get(self):
        with CursorManager() as cursor:
            exam_line = table_manager(ExamLine)
            exam_line_infos = exam_line.query_records(cursor)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'exam_line': exam_line_infos,
            }))

@app.route(r'/api/admin/examline')
class AdminSaveLine(web.RequestHandler):
    def get(self):
        lineid = self.get_argument('lineid', None)
        if lineid:
            with CursorManager() as cursor:
                exam_line = table_manager(ExamLine)
                exam_line_info = exam_line.query_record(cursor, id=lineid)
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功',
                    'exam_line': exam_line_info,
                }))
        else:
            self.write(json.dumps({
                'state': 2,
                'message': '失败',
            }))

    def post(self):
        lineid = self.get_argument('lineid', None)
        name = self.get_argument('name', None)
        points = self.get_argument('points', None)

        if name is None:
            self.write(json.dumps({
                'state': 3,
                'message': '名字不能为空！'
            }))
            return

        with CursorManager() as cursor:
            exam_line = table_manager(ExamLine)

            result = None
            if lineid:
                result = exam_line.update_record(cursor, lineid, name=name, points=points)
            else:
                result = exam_line.new_record(cursor, name=name)
            
            if result:
                self.write(json.dumps({
                    'state': 1,
                    'message': '成功'
                }))
            else:
                self.write(json.dumps({
                    'state': 2,
                    'message': '创建失败'
                }))

class AdminImportUsers(web.RequestHandler):
    def post(self):
        pass

# 初始化数据库

@app.route(r'/admin/init')
class AdminInit(web.RequestHandler):
    def get(self):
        print(self.request)
        if self.request.remote_ip == '127.0.0.1' or self.request.remote_ip == '::1':
            init_db()
            self.write('OK')
        else:
            self.write('no permission')

