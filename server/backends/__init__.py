#!/usr/bin/python
#coding:utf-8

from datetime import datetime
import hashlib
import json

import sqlite3
import redis


conn = sqlite3.connect('server/db/demo.db')
r_conn = redis.Redis()

class Session(object):
    def __init__(self):
        super(Session, self).__init__()
        self.redis_prefix = 'session_'

    def get_session_id(self, user_info):
        username = user_info.get('username')

        session_id = username + datetime.now().isoformat()
        session_id = session_id.encode('utf-8')
        session_id = hashlib.md5(session_id).hexdigest()

        r_conn.set(self.redis_prefix + session_id, json.dumps(user_info), ex=86400)
        return session_id

    def is_login(self, session_id):
        return r_conn.get(self.redis_prefix + session_id) is not None

    def get_user_info(self, session_id):
        user_info = r_conn.get(self.redis_prefix + session_id)

        return json.loads(user_info) if user_info else None


class CursorManager(object):
    def __init__(self, connect=None):
        global conn

        self._conn = connect or conn

    def __enter__(self):
        self._cursor = self._conn.cursor()
        return self._cursor

    def __exit__(self, type, value, trace):
        self._cursor.close()

def init_db():
    with conn:
        # 考试表 state: (1: 初始化， 2: 考试)
        conn.execute('''
            CREATE TABLE exam (
                id INTEGER PRIMARY KEY,
                name VARCHAR(40),
                username VARCHAR(20),
                state INTEGER,
                create_time TIMESTAMP
            );
        ''');
        # 考试用户表
        conn.execute('''
            CREATE TABLE exam_user (
                id INTEGER PRIMARY KEY,
                exam_id INTEGER,
                line_id INTEGER,
                device_id VARCHAR(20),
                username VARCHAR(20),
                score DOUBLE,
                create_time TIMESTAMP
            );
        ''');
        conn.execute('CREATE INDEX exam_user_exam ON exam_user (exam_id);')
        conn.execute('CREATE INDEX exam_user_line ON exam_user (line_id);')
        conn.execute('CREATE INDEX exam_user_device ON exam_user (device_id);')
        # 考试路线表
        conn.execute('''
            CREATE TABLE exam_line (
                id INTEGER PRIMARY KEY,
                name VARCHAR(20),
                points TEXT,
                valid INTEGER,
                create_time TIMESTAMP
            );
        ''')
        # 后台用户表
        conn.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY,
                username VARCHAR(20),
                nickname VARCHAR(20),
                password VARCHAR(40),
                valid INTEGER,
                create_time TIMESTAMP,
                update_time TIMESTAMP,
                remark VARCHAR(250)
            );
        ''')

        # 创建记录
        conn.execute('''
            INSERT INTO user (username, nickname, password, valid, create_time, update_time) values
            (?, ?, ?, ?, ?, ?)
        ''', ('admin', '管理员', hashlib.md5(b'123456').hexdigest(), 1, datetime.now().isoformat(), datetime.now().isoformat()))

def dict_factory(cursor, row):  
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn.row_factory = dict_factory

def _query_object(cursor, table, fields, **kwargs):
    if kwargs:
        val = [(kv[0] + '="' + str(kv[1]) + '"') for kv in kwargs.items()]
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

class BaseTable(object):
    def __init__(self, table):
        super(BaseTable, self).__init__()
        self._table = table

    def _query_record(self, cursor, fields, **kwargs):
        if kwargs:
            val = [(kv[0] + '="' + str(kv[1]) + '"') for kv in kwargs.items()]
        else:
            val = ['1=1']

        try:
            sql_str = '''
                SELECT %s FROM %s WHERE %s
            ''' % (', '.join(fields), self._table, ' and '.join(val))
            cursor.execute(sql_str)
            return cursor.fetchall()
        except Exception as e:
            raise e
        return None

    def _new_record(self, cursor, **kwargs):
        sql_str = '''
            INSERT INTO %s (%s) values (%s);
        ''' % (self._table, ', '.join(kwargs.keys()), ('?, ' * len(kwargs))[:-2])

        record_id = None
        try:
            cursor.execute(sql_str, tuple(kwargs.values()))
            record_id = cursor.lastrowid
            cursor.connection.commit()
        except Exception as e:
            print(e)
        return record_id

    def _new_records(self, cursor, fields, records):
        sql_str = '''
            INSERT INTO %s (%s) values (%s);
        ''' % (self._table, ', '.join(fields), ('?, ' * len(fields))[:-2])

        try:
            cursor.executemany(sql_str, records)
            record_id = cursor.lastrowid
            cursor.connection.commit()
        except Exception as e:
            pass
        return record_id

    def _update_record(self, cursor, record_id, **kwargs):
        sql_str = '''
            UPDATE %s SET %s WHERE id=?
        ''' % (self._table, '=?,'.join(kwargs.keys()) + '=?')

        try:
            values = kwargs.values()
            values.append(record_id)
            cursor.execute(sql_str, values)
        except Exception as e:
            raise e

class Exam(BaseTable):
    def __init__(self):
        super(Exam, self).__init__('exam')

    def new_record(self, cursor, name):
        return self._new_record(cursor, name=name, state=1, create_time=datetime.now().isoformat())

    def query_records(self, cursor, **kwargs):
        return self._query_record(cursor, ('id', 'name', 'username', 'state', 'create_time'), **kwargs)

    def query_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'username', 'state', 'create_time'), **kwargs)
        if result:
            return result[0]
        else:
            return None

class ExamUser(BaseTable):
    def __init__(self):
        super(ExamUser, self).__init__('exam_user')

    def import_records(self, cursor, users):
        time_now = [datetime.now().isoformat()]

        users = [user + time_now for user in users]
        self._new_records(cursor, ['exam_id', 'line_id', 'device_id', 'username', 'create_time'], users)

    def update_record(self, cursor, record_id, **kwargs):
        self._update_record(cursor, record_id, **kwargs)

    def query_records(self, cursor, **kwargs):
        return self._query_record(cursor, ('id', 'exam_id', 'line_id', 'device_id', 'username', 'score'), **kwargs)

class ExamLine(BaseTable):
    def __init__(self):
        super(ExamLine, self).__init__('exam_line')

    def new_record(self, cursor, name):
        return self._new_record(cursor, name=name, valid=2, create_time=datetime.now().isoformat())

    def query_records(self, cursor, **kwargs):
        return self._query_record(cursor, ('id', 'name', 'valid'), **kwargs)

    def query_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'points'), **kwargs)
        if result:
            return result[0]
        else:
            return None

    def update_record(self, cursor, id, **kwargs):
        return self._update_record(cursor, id, valid=1, **kwargs)

class User(BaseTable):
    def __init__(self):
        super(User, self).__init__('user')

    def new_record(self, cursor, username, nickname, password):
        return self._new_record(cursor, username=username,
            nickname=nickname, password=password, create_time=datetime.now().isoformat(),
            update_time=datetime.now().isoformat())

    def query_records(self, cursor, **kwargs):
        return self._query_record(cursor, ('id', 'nickname', 'username', 'update_time', 'create_time'), **kwargs)

    def query_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'nickname', 'username', 'password', 'create_time'), **kwargs)
        if result:
            return result[0]
        else:
            return None

class UserRecord(BaseTable):
    def __init__(self, ext_name):
        super(UserRecord, self).__init__('user_record_' + ext_name)
        

def create_exam(cursor, name):
    sql_str = '''
        INSERT INTO exam (name, state, create_time) values (?, 1, ?);
    '''

    exam_id = None
    try:
        cursor.execute(sql_str, (name, datetime.now().isoformat()))
        exam_id = cursor.lastrowid
        cursor.connection.commit()
    except Exception as e:
        pass
    return exam_id

def query_exams(cursor, **kwargs):
    return _query_object(cursor, 'exam', ('id', 'name', 'username', 'state', 'create_time'), **kwargs)

def query_exam(cursor, **kwargs):
    result = _query_object(cursor, 'exam', ('id', 'name', 'username', 'state', 'create_time'), **kwargs)
    if result:
        return result[0]
    else:
        return None

def add_exam_users(cursor, exam_id, users):
    try:
        for user in users:
            sql_str = '''
                INSERT INTO exam_user (exam_id, line_id, device_id, username, create_time) values (?, ?, ?, ?, ?)
            ''' % (exam_id, 1, user.get('device_id'), user.get('username'), datetime.now().isoformat())
            cursor.execute(sql_str)
        cursor.connection.commit()
    except Exception as e:
        raise e

def query_exam_user(cursor, **kwargs):
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


def add_user(cursor, username, password, nickname):
    try:
        sql_str = '''
            INSERT INTO user (username, nickname, password, create_time, update_time, valid) values (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(sql_str, (username, nickname, password, datetime.now().isoformat(), datetime.now().isoformat(), 1))
        cursor.connection.commit()
    except Exception as e:
        return False
    return True

def query_user(cursor, username):
    users = _query_object(cursor, 'user', ('id', 'username', 'nickname', 'password'), username=username, valid=1)
    return users[0] if users else None

def query_all_user(cursor):
    return _query_object(cursor, 'user', ('id', 'username', 'nickname', 'create_time', 'update_time'), valid=1)

def update_user_password(cursor, user_id, password):
    sql_str = '''
        UPDATE user SET password, update_time) values (?, ?) WHERE id=?;
    ''' % (password, datetime.now().isoformat(), user_id)

    result = False
    try:
        cursor.execute(sql_str)
        cursor.connection.commit()
        result = True
    except Exception as e:
        pass
    return result


_table_map = dict()
def table_manager(table, ext_name=None, **kwargs):
    global _table_map

    table_name = str(table).split('.')[-1]
    table_name = table_name + '_' + ext_name if ext_name else table_name

    if not _table_map.get(table_name):
        obj = table(ext_name) if ext_name else table()
        _table_map.update({table_name: obj})
    return _table_map.get(table_name)
        

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
        # print(query_exam(cursor))
        exam = Exam()
        print(exam.query_records(cursor))

