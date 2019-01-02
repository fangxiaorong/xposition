#!/usr/bin/python
#coding:utf-8




import os
from datetime import datetime

import json
import sqlite3
from tornado import web
import functools

from backends import *

### 启动
exam_id = table_manager(Exam).get_active_id()
if exam_id:
    table_manager(UserRecord, str(exam_id), True)
###

ERR_MSG_MAP = {
    'DB_1': '成功',
    'DB_10': '记录重复',
    'DB_1000': '考试人员不能为空',
    'DB_1001': '考试已经考试完毕',
    'DB_1002': '起止时间不能为空',
    'DB_1003': '不在考试范围内',
}

def auth_check(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        session_id = self.get_secure_cookie("session_id")
        self.user_info = session.get_user_info(session_id.decode('utf-8')) if session_id else None
        if self.user_info:
            return method(self, *args, **kwargs)
        else:
            self.write(json.dumps({
                'state': 2000,
                'message': '用户未登陆',
            }))
    return wrapper

class BaseHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/x-www-form-urlencoded')

class RouteConfig(web.Application):
    def route(self, url):
        def register(handler):
            self.add_handlers('.*$', [(url, handler)])
            return handler
        return register

app = RouteConfig(cookie_secret='Zxyo8feo0Ujlx', xsrf_cookies=False, debug=True)
session = Session()

@app.route(r'/')
class HomeIndex(web.RequestHandler):
    def get(self):
        self.write('Hello')

# 用户端接口

@app.route(r'/api/user/login/([^/]*)')
class UserLogin(BaseHandler):
    def get(self, device_id):
        exam = table_manager(Exam)
        active_id = exam.get_active_id()
        if active_id >= 0:
            with CursorManager() as cursor:
                exam_user = table_manager(ExamUser)
                users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)
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
        else:
            self.write(json.dumps({
                'state': 3,
                'message': '暂未设置考试'
            }))

@app.route(r'/api/user/autologin')
class UserAutoLogin(BaseHandler):
    def get(self):
        device_id = self.get_argument('device_id')
        exam = table_manager(Exam)
        active_id = exam.get_active_id()
        if active_id >= 0:
            with CursorManager() as cursor:
                exam_user = table_manager(ExamUser)
                users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)
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
        else:
            self.write(json.dumps({
                'state': 3,
                'message': '暂未设置考试'
            }))

    def post(self):
        device_id = self.get_argument('device_id')
        line_id = self.get_argument('line_id')
        username = self.get_argument('username')
        departname = self.get_argument('departname')

        active_id = table_manager(Exam).get_active_id()
        if active_id >= 0:
            with CursorManager() as cursor:
                exam_user = table_manager(ExamUser)
                users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)
                if users:
                    self.write(json.dumps({
                        'state': 10,
                        'message': '用户已存在'
                    }))
                else:
                    user = {
                        'exam_id': active_id,
                        'line_id': int(line_id),
                        'device_id': device_id,
                        'username': username,
                        'departname': departname,
                    }
                    exam_user.new_record(cursor, user)

                    users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)
                    if users:
                        self.write(json.dumps({
                            'state': 1,
                            'message': '成功',
                            'user': users[0]
                        }))
                    else:
                        self.write(json.dumps({
                            'state': 4,
                            'message': '用户创建失败'
                        }))
        else:
            self.write(json.dumps({
                'state': 3,
                'message': '暂未设置考试'
            }))


@app.route(r'/api/user/position')
class UserUploadPosition(web.RequestHandler):
    def post(self):
        exam_id = table_manager(Exam).get_active_id()
        if exam_id:
            user_record = table_manager(UserRecord, str(exam_id), False)
            if user_record:
                user_id = int(self.get_argument('user_id'))
                latitude = float(self.get_argument('latitude'))
                longitude = float(self.get_argument('longitude'))
                manual = int(self.get_argument('manual'))
                user_record.add_record(user_id, latitude, longitude, manual)

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

@app.route(r'/api/manager/exam')
class ManagerGetExam(BaseHandler):
    @auth_check
    def get(self):
        exam = table_manager(Exam)
        active_id = exam.get_active_id()
        if active_id >= 0:
            with CursorManager() as cursor:
                exam_info, active_id = exam.query_record(cursor, id=active_id)
                if exam_info:
                    self.write(json.dumps({
                        'state': 1,
                        'message': '成功',
                        'info': exam_info,
                        'active_id': active_id,
                    }))
                else:
                    self.write(json.dumps({
                        'state': 2,
                        'message': '数据为空',
                    }))
        else:
            self.write(json.dumps({
                'state': 3,
                'message': '考试未设置',
            }))

@app.route(r'/api/manager/locations')
class ManagerGetLocations(web.RequestHandler):
    @auth_check
    def get(self):
        exam_user = table_manager(ExamUser)
        locations = exam_user.query_locations()
        if locations:
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
class ManagerGetUserTrack(BaseHandler):
    def get(self, user_id):
        start = int(self.get_argument('start', 0))
        end = int(self.get_argument('end', 0))

        exam_id = table_manager(Exam).get_active_id()
        if exam_id:
            user_record = table_manager(UserRecord, str(exam_id), False)
            points = user_record.query_records(int(user_id), start=start / 1000.0, end=end / 1000.0)

            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'points': points
            }))
        else:
            self.write(json.dumps({
                'state': 10,
                'message': '无考试记录'
            }))

@app.route(r'/api/manager/user/result/(\d+)')
class ManagerGetUserResult(web.RequestHandler):
    def get(self, user_id):
        data = {'state': 2, 'message': '用户未找到'}
        with CursorManager() as cursor:
            user_info_list = table_manager(ExamUser).query_detail_records(cursor, id=user_id)
            if user_info_list:
                user_info = user_info_list[0]
                if user_info.get('detail'):
                    user_info.update({'detail': json.loads(user_info.get('detail'))})
                    data.update(user_info)
                    data.update({'state': 1, 'message': '成功'})
                else:
                    data.update({'state': 3, 'message': '请先计算考试结果'})
        print(data)
        self.write(json.dumps(data))

@app.route(r'/api/manager/user/results')
class ManagerUserResults(web.RequestHandler):
    def get(self):
        results = {}

        active_id = table_manager(Exam).get_active_id()
        if active_id > 0:
            with CursorManager() as cursor:
                exam_info, active_id = table_manager(Exam).query_record(cursor, id=active_id)
                level1 = exam_info.get('level1') or 0
                level2 = exam_info.get('level2') or 0
                level3 = exam_info.get('level3') or 0
                level4 = exam_info.get('level4') or 0

                print(exam_info)
                results.update({'examname': exam_info.get('name'),'level1': level1, 'level2': level2, 'level3': level3, 'level4': level4})

                if level1 > 0 and level2 > 0 and level3 > 0 and level4 > 0:
                    user_info_list = table_manager(ExamUser).query_detail_records(cursor, exam_id=active_id)
                    users = []
                    for user_info in user_info_list:
                        if not user_info.get('detail'):
                            continue

                        users.append(json.loads(user_info.get('detail')))
                    users.sort(key=lambda user: user['total_score'], reverse=True)
                    results.update({'users': users})
        results.update({'state': 1, 'message': '成功'})
        self.write(json.dumps(results))

    def post(self):
        level1 = self.get_argument('level1', 0)
        level2 = self.get_argument('level2', 0)
        level3 = self.get_argument('level3', 0)
        level4 = self.get_argument('level4', 0)

        data = ExamCalculate.calculate_all(float(level1), float(level2), float(level3), float(level4))
        users = data.get('users')
        users.sort(key=lambda user: user['total_score'], reverse=True)
        data.update({
            'state': 1,
            'message': '成功',
            'users': users
        })
        self.write(json.dumps(data))

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
class AdminExam(BaseHandler):
    @auth_check
    def post(self):
        exam_id = self.get_argument('exam_id', None)
        exam_name = self.get_argument('name', None)
        score1 = self.get_argument('score1', 0)
        score2 = self.get_argument('score2', 0)
        score3 = self.get_argument('score3', 0)
        score4 = self.get_argument('score4', 0)
        starttime = self.get_argument('starttime', '')
        endtime = self.get_argument('endtime', '')

        with CursorManager() as cursor:
            exam = table_manager(Exam)

            result = -1
            if exam_id is not None:
                if score1 == 0:
                    result = exam.update_active(cursor, exam_id)
                else:
                    result = exam.update_record(cursor, exam_id, score1=score1, score2=score2, score3=score3, score4=score4, starttime=starttime, endtime=endtime)
            else:
                result = exam.new_record(cursor, exam_name, score1=score1, score2=score2, score3=score3, score4=score4, starttime=starttime, endtime=endtime)

            print(result)
            self.write(json.dumps({
                'state': result,
                'message': ERR_MSG_MAP.get('DB_' + str(result)) or '失败'
            }))

@app.route(r'/api/admin/exams')
class AdminGetExams(BaseHandler):
    @auth_check
    def get(self):
        with CursorManager() as cursor:
            exam = table_manager(Exam)
            exam_infos, active_exam_id = exam.query_records(cursor)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'exams': exam_infos,
                'active_exam_id': active_exam_id,
            }))

# @app.route(r'/api/admin/exam/(\d+)')
# class AdminGetExam(BaseHandler):
#     def get(self, exam_id):
#         with CursorManager() as cursor:
#             exam, active_exam_id = quer_exam(cursor, id=exam_id)
#             self.write(json.dumps({
#                 'state': 1,
#                 'message': '成功',
#                 'exam': exam,
#                 'active_exam_id': active_exam_id,
#             }))

@app.route(r'/api/admin/examuser/list/(\d+)')
class AdminGetExamUser(BaseHandler):
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

    # @auth_check
    # def post(self, exam_id):
    #     exam_users = self.get_argument('exam_users', None)

    #     if exam_users and exam_id:
    #         exam_users = json.loads(exam_users)
    #         with CursorManager() as cursor:
    #             exam_user = table_manager(ExamUser)
    #             exam_user.delete_record(cursor, exam_id=exam_id)
    #             exam_user.import_records(cursor, exam_users)

    #         self.write(json.dumps({
    #             'state': 1,
    #             'message': '成功',
    #         }))
    #     else:
    #         self.write(json.dumps({
    #             'state': 10,
    #             'message': '失败'
    #         }))

    @auth_check
    def post(self, exam_id):
        exam_user_info = self.get_argument('exam_user', None)

        if exam_user_info and exam_id:
            exam_user_info = json.loads(exam_user_info)
            with CursorManager() as cursor:
                exam_user = table_manager(ExamUser)
                update_user_info = {
                    'exam_id': exam_user_info.get('exam_id'),
                    'line_id': exam_user_info.get('line_id'),
                    'device_id': exam_user_info.get('device_id'),
                    'username': exam_user_info.get('username'),
                    'departname': exam_user_info.get('departname'),
                    'score': exam_user_info.get('score')
                }
                exam_user.update_record(cursor, exam_user_info.get('id'), **update_user_info)
                # exam_user_infos = exam_user.query_records(cursor, exam_id=exam_id)
                # for item in exam_user_infos:
                #     if item.get('device_id') == exam_user_info.get('device_id'):
                #         item.update(exam_user_info)
                #         break
                #         print(exam_user_infos, exam_user_info)
                # exam_user.delete_record(cursor, exam_id=exam_id)
                # exam_user.import_records(cursor, exam_users)

            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'user_info': exam_user_info
            }))
        else:
            self.write(json.dumps({
                'state': 10,
                'message': '失败'
            }))

@app.route(r'/api/admin/examline/list')
class AdminGetExamLines(BaseHandler):
    # @auth_check
    def get(self):
        valid = self.get_argument('valid', None)

        with CursorManager() as cursor:
            exam_line = table_manager(ExamLine)
            exam_line_infos = exam_line.query_records(cursor) if valid is None else exam_line.query_records(cursor, valid=valid)
            self.write(json.dumps({
                'state': 1,
                'message': '成功',
                'exam_line': exam_line_infos,
            }))

@app.route(r'/api/admin/examline')
class AdminExamLine(BaseHandler):
    @auth_check
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

    @auth_check
    def post(self):
        lineid = self.get_argument('lineid', None)
        name = self.get_argument('name', None)
        points = self.get_argument('points', None)
        valid = self.get_argument('valid', None)

        if name is None and lineid is None:
            self.write(json.dumps({
                'state': 3,
                'message': '名字不能为空！'
            }))
            return

        with CursorManager() as cursor:
            exam_line = table_manager(ExamLine)

            result = None
            if lineid:
                kwargs = {}
                if name is not None:
                    kwargs.update({'name': name})
                if points is not None:
                    # check weight
                    from  decimal import Decimal
                    tmp = 0
                    for point in json.loads(points):
                        tmp += Decimal(point.get('weight')) if point.get('weight') else Decimal(0)
                    print(tmp)
                    if tmp != Decimal(1.0):
                        self.write(json.dumps({
                            'state': 4,
                            'message': '权重设置错误！'
                        }))
                        return
                    # end check

                    kwargs.update({'points': points})
                if valid is not None:
                    kwargs.update({'valid': valid})
                result = exam_line.update_record(cursor, int(lineid), **kwargs)
            else:
                result = exam_line.new_record(cursor, name=name)
            
            self.write(json.dumps({
                'state': result,
                'message': ERR_MSG_MAP.get('DB_' + str(result)) or '创建失败'
            }))

# 初始化数据库

@app.route(r'/api/admin/init')
class AdminInit(web.RequestHandler):
    def get(self):
        print(self.request)
        if self.request.remote_ip == '127.0.0.1' or self.request.remote_ip == '::1':
            init_db()
            self.write('OK')
        else:
            self.write('no permission')

