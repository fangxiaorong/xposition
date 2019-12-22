#!/usr/bin/python
#coding:utf-8

from datetime import datetime
import time
import hashlib
import json
import math

import sqlite3
import MySQLdb
import redis

import settings

try:
    config = settings.DB_CONFIG.get('default') if hasattr(settings, 'DB_CONFIG') else {}
    if config.get('type') == 'sqlite':
        conn = sqlite3.connect(config.get('path', 'server/db/main.db'))
    elif config.get('type') == 'mysql':
        conn = MySQLdb.connect(config.get('host'), config.get('username'), config.get('password'), config.get('db'), charset='utf8')
except Exception as e:
    raise e

r_conn = redis.Redis()

sql_result_map = {
    'SUCCESS': 1,
    'UNIQUE constraint failed': 10,
}

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
    with conn.cursor() as cursor:
        # 考试表 state: (1: 初始化， 2: 考试)
        cursor.execute('''
            CREATE TABLE exam (
                id INTEGER PRIMARY KEY,
                name VARCHAR(40) UNIQUE,
                username VARCHAR(20),
                level1 DOUBLE,
                level2 DOUBLE,
                level3 DOUBLE,
                level4 DOUBLE,
                score1 DOUBLE,
                score2 DOUBLE,
                score3 DOUBLE,
                score4 DOUBLE,
                starttime TIMESTAMP,
                endtime TIMESTAMP,
                state INTEGER,
                create_time TIMESTAMP
            );
        ''');
        # 考试用户表
        cursor.execute('''
            CREATE TABLE exam_user (
                id INTEGER PRIMARY KEY,
                exam_id INTEGER,
                line_id INTEGER,
                device_id VARCHAR(20),
                username VARCHAR(20),
                departname VARCHAR(200),
                score DOUBLE,
                detail TEXT,
                create_time TIMESTAMP
            );
        ''');
        cursor.execute('CREATE INDEX exam_user_exam ON exam_user (exam_id);')
        cursor.execute('CREATE INDEX exam_user_line ON exam_user (line_id);')
        cursor.execute('CREATE INDEX exam_user_device ON exam_user (device_id);')
        # 考试路线表
        cursor.execute('''
            CREATE TABLE exam_line (
                id INTEGER PRIMARY KEY,
                name VARCHAR(20) UNIQUE,
                points TEXT,
                valid INTEGER,
                create_time TIMESTAMP
            );
        ''')
        # 后台用户表
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY,
                username VARCHAR(20) UNIQUE,
                nickname VARCHAR(20),
                password VARCHAR(40),
                valid INTEGER,
                create_time TIMESTAMP,
                update_time TIMESTAMP,
                remark VARCHAR(250)
            );
        ''')

        # 创建记录
        cursor.execute('''
            INSERT INTO user (username, nickname, password, valid, create_time, update_time) values
            (?, ?, ?, ?, ?, ?)
        ''', ('admin', '管理员', hashlib.md5(b'123456').hexdigest(), 1, datetime.now().isoformat(), datetime.now().isoformat()))

def dict_factory(cursor, row):  
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn.row_factory = dict_factory

class BaseTable(object):
    def __init__(self, table):
        super(BaseTable, self).__init__()
        self._table = table

    def _query_record(self, cursor, fields, orderby='', **kwargs):
        if kwargs:
            val = [(kv[0] + '="' + str(kv[1]) + '"') if kv[1] is not None else (kv[0] + ' is not null') for kv in kwargs.items()]
        else:
            val = ['1=1']

        try:
            sql_str = '''
                SELECT %s FROM %s WHERE %s %s
            ''' % (', '.join(fields), self._table, ' and '.join(val), orderby)
            cursor.execute(sql_str)
            return cursor.fetchall()
        except Exception as e:
            # result = sql_result_map.get(e.args[0].split(':')[0])
            # if not result:
            #     result = (100, '失败')
            print(e)
        return None

    def _new_record(self, cursor, **kwargs):
        sql_str = '''
            INSERT INTO %s (%s) values (%s);
        ''' % (self._table, ', '.join(kwargs.keys()), ('?, ' * len(kwargs))[:-2])

        result = sql_result_map.get('SUCCESS')
        try:
            cursor.execute(sql_str, tuple(kwargs.values()))
            record_id = cursor.lastrowid
            cursor.connection.commit()
        except Exception as e:
            result = sql_result_map.get(e.args[0].split(':')[0])
            if not result:
                result = (100, '失败')
        return result

    def _new_records(self, cursor, fields, records):
        sql_str = '''
            INSERT INTO %s (%s) values (%s);
        ''' % (self._table, ', '.join(fields), ('?, ' * len(fields))[:-2])

        result = sql_result_map.get('SUCCESS')
        try:
            cursor.executemany(sql_str, records)
            cursor.connection.commit()
        except Exception as e:
            result = sql_result_map.get(e.args[0].split(':')[0])
            if not result:
                result = (100, '失败')
        return result

    def _update_record(self, cursor, record_id, **kwargs):
        sql_str = '''
            UPDATE %s SET %s WHERE id=?
        ''' % (self._table, '=?,'.join(kwargs.keys()) + '=?')

        result = sql_result_map.get('SUCCESS')
        try:
            values = [v for v in kwargs.values()]
            values.append(record_id)
            print(sql_str, values)
            cursor.execute(sql_str, tuple(values))
            cursor.connection.commit()
        except Exception as e:
            print(e)
            result = sql_result_map.get(e.args[0].split(':')[0])
            if not result:
                result = (100, '失败')
        return result

    def _delete_record(self, cursor, **kwargs):
        sql_str = '''
            DELETE FROM %s WHERE %s
        ''' % (self._table, '=? and '.join(kwargs.keys()) + '=?')

        result = sql_result_map.get('SUCCESS')
        try:
            return cursor.execute(sql_str, tuple(kwargs.values()))
        except Exception as e:
            result = sql_result_map.get(e.args[0].split(':')[0])
            if not result:
                result = (100, '失败')
        return result

class Exam(BaseTable):
    def __init__(self):
        super(Exam, self).__init__('exam')
        self._exam_active_id = 'exam_active_id'

    def new_record(self, cursor, name, **kwargs):
        return self._new_record(cursor, name=name, state=1, create_time=datetime.now().isoformat(), **kwargs)

    def query_records(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'level1', 'level2', 'level3', 'level4', 'score1', 'score2', 'score3', 'score4', 'starttime', 'endtime', 'state', 'create_time'), **kwargs)
        if result:
            active_item_id = r_conn.hget(self._exam_active_id, '-1') or b'-1'
            active_item_id = int(active_item_id)
            print(active_item_id)
        else:
            active_item_id = -1
        return (result, active_item_id)

    def query_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'level1', 'level2', 'level3', 'level4', 'score1', 'score2', 'score3', 'score4', 'starttime', 'endtime', 'state', 'create_time'), **kwargs)
        if result:
            active_item_id = r_conn.hget(self._exam_active_id, '-1') or b'-1'
            active_item_id = int(active_item_id)
            return (result[0], active_item_id)
        else:
            return (None, -1)

    def update_record(self, cursor, exam_id, **kwargs):
        result = self._update_record(cursor, exam_id, **kwargs)
        return result

    def update_active(self, cursor, exam_id, **kwargs):
        result = -1

        if not r_conn.hexists(self._exam_active_id, str(exam_id)):
            exam_info, _ = table_manager(Exam).query_record(cursor, id=exam_id)
            starttime = -1
            endtime = -1
            current_time = datetime.now().timestamp()
            try:
                starttime = datetime.strptime(exam_info.get('starttime'), '%Y-%m-%d %H:%M:%S').timestamp()
                endtime = datetime.strptime(exam_info.get('endtime'), '%Y-%m-%d %H:%M:%S').timestamp()
            except Exception as e:
                pass
            print(starttime, endtime, current_time)
            if starttime <= 0 or endtime <= 0:
                result = 1002 
            elif current_time <= starttime or current_time > endtime:
                result = 1003 
            else:
                exam_user = table_manager(ExamUser)
                # if len(exam_user.query_records(cursor, exam_id=exam_id)) > 0:
                self._update_record(cursor, exam_id, state=2, **kwargs)
                r_conn.hmset(self._exam_active_id, {str(exam_id): 1, '-1': exam_id})

                exam_user.update_active(cursor, exam_id)

                result = 1
                # else:
                    # result = 1 #1000
                pass
        else:
            result = 1001
        return result

    def get_active_id(self):
        active_id = r_conn.hget(self._exam_active_id, '-1')
        return int(active_id) if active_id is not None else -1

class ExamUser(BaseTable):
    def __init__(self):
        super(ExamUser, self).__init__('exam_user')

    def import_records(self, cursor, users):
        time_now = datetime.now().isoformat()

        users = [(user.get('exam_id'), user.get('line_id'), user.get('device_id'), user.get('username'), user.get('departname'), time_now) for user in users]
        return self._new_records(cursor, ['exam_id', 'line_id', 'device_id', 'username', 'departname', 'create_time'], users)

    def update_record(self, cursor, record_id, **kwargs):
        active_id = table_manager(Exam).get_active_id()
        if kwargs['exam_id'] == active_id:
            pos_str = r_conn.hget('active_user_info', record_id)
            if pos_str:
                att = json.loads(pos_str)
                data = kwargs.get('line_id') or att.get('line_id')
                if data:
                    att['line_id'] = data
                data = kwargs.get('username') or att.get('username')
                if data:
                    att['username'] = data
                data = kwargs.get('departname') or att.get('departname')
                if data:
                    att['departname'] = data
                data = kwargs.get('detail') or att.get('detail')
                if data:
                    att['detail'] = data
                pos_str = json.dumps(att)
                r_conn.hset('active_user_info', record_id, pos_str)

        self._update_record(cursor, record_id, **kwargs)

    def query_records(self, cursor, **kwargs):
        exam_users = self._query_record(cursor, ('id', 'exam_id', 'line_id', 'device_id', 'username', 'departname', 'score'), **kwargs)
        if exam_users:
            line_dict = {}
            try:
                line_ids = []
                for exam_user in exam_users:
                    line_id = exam_user.get('line_id')
                    if line_id is not None:
                        line_ids.append(str(line_id))
                if len(line_ids) > 0:
                    sql_str = '''
                        SELECT id, name FROM exam_line WHERE id in (%s)
                    ''' % (', '.join(line_ids))
                    cursor.execute(sql_str)
                    for line in cursor.fetchall():
                        line_dict.update({line.get('id'): line})
            except Exception as e:
                print(e)
            for exam in exam_users:
                line_id = exam.get('line_id')
                if line_id:
                    exam.update({'line': line_dict.get(exam.get('line_id'))})
        return exam_users

    def query_detail_records(self, cursor, **kwargs):
        exem_detail_users = self._query_record(cursor, ('id', 'username', 'departname', 'detail'), **kwargs)

        return exem_detail_users

    def new_record(self, cursor, user):
        user_info = {
            'exam_id': user.get('exam_id'),
            'line_id': user.get('line_id'),
            'device_id': user.get('device_id'),
            'username': user.get('username'),
            'departname': user.get('departname'),
            'create_time': datetime.now().isoformat(),
        }
        result = self._new_record(cursor, **user_info)
        user_id = cursor.lastrowid

        active_id = table_manager(Exam).get_active_id()
        if user.get('exam_id') == active_id:
            pos_str = json.dumps({'user_id': user_id, 'line_id': user.get('line_id'), 'username': user.get('username')})
            r_conn.hset('active_user_info', user_id, pos_str)

        return result

    def delete_record(self, cursor, exam_id):
        return self._delete_record(cursor, exam_id=exam_id)

    def update_active(self, cursor, exam_id):
        exam_user_infos = self.query_records(cursor, exam_id=exam_id)
        user_record = table_manager(UserRecord, str(exam_id))
        user_record.create_table()

        user_ids = r_conn.hgetall(user_record.active_user_info_key)
        del_keys = [user_record.record_prefix + user_id.decode('utf-8') for user_id in user_ids]
        del_keys.append(user_record.active_user_info_key)
        r_conn.delete(*tuple(del_keys))

        if len(exam_user_infos) > 0:
            info_map = {} # {'exam_id': exam_id}
            for user_info in exam_user_infos:
                info_map.update({user_info.get('id'): json.dumps({'username': user_info.get('username')})})
            print(info_map)
            r_conn.hmset(user_record.active_user_info_key, info_map)
        else:
            r_conn.delete(user_record.active_user_info_key)

    def query_locations(self):
        result = []

        user_pos_arr = r_conn.hgetall('active_user_info')
        current_time = time.time()
        for user_pos in user_pos_arr.values():
            user_pos = user_pos.decode('utf-8')
            if user_pos != '':
                pos_info = json.loads(user_pos)
                tmp_time = float(pos_info.get('create_time')) if pos_info.get('create_time') else 0
                if current_time - tmp_time < 300:
                    pos_info.update({'state': 1})
                else:
                    pos_info.update({'state': 2})
                result.append(pos_info)

        return result

    def query_result(self, user_id):
        exam_users = self._query_record(cursor, ('id', 'exam_id', 'line_id', 'device_id', 'username', 'score'), **kwargs)

class ExamLine(BaseTable):
    def __init__(self):
        super(ExamLine, self).__init__('exam_line')

    def new_record(self, cursor, name):
        return self._new_record(cursor, name=name, valid=2, create_time=datetime.now().isoformat())

    def query_records(self, cursor, **kwargs):
        return self._query_record(cursor, ('id', 'name', 'valid'), **kwargs)

    def query_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'points', 'valid'), **kwargs)
        if result:
            return result[0]
        else:
            return None

    def update_record(self, cursor, id, **kwargs):
        if kwargs.get('valid') is None:
            kwargs.update({'valid': 1})
        return self._update_record(cursor, id, **kwargs)

    def query_postion_record(self, cursor, **kwargs):
        result = self._query_record(cursor, ('id', 'name', 'points'), **kwargs)
        if result:
            result = result[0]
            points = json.loads(result.get('points', '[]'))
            for point in points:
                latitude, longitude = ExamCalculate.dd2k_to_amap(float(point.pop('x')), float(point.pop('y')))
                point.update({'latitude': latitude, 'longitude': longitude})
            result.update({'points': json.dumps(points)})
            return result

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
        self.record_prefix = 'user_pos_'
        self.active_user_info_key = 'active_user_info'
    
    def create_table(self):
        conn.execute('''
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                latitude DOUBLE,
                longitude DOUBLE,
                manual INTEGER,
                create_time DOUBLE
            );
        ''' % self._table);

    def add_record(self, user_id, latitude, longitude, manual=0):
        if latitude <= 0 or longitude <= 0:
            return

        key = self.record_prefix + str(user_id)

        info = r_conn.hget(self.active_user_info_key, user_id)
        if info is not None:
            info = json.loads(info)
            pos_str = json.dumps({'user_id': user_id, 'line_id': info.get('line_id'), 'username': info.get('username'), 'latitude': latitude, 'longitude': longitude, 'manual': manual, 'create_time': time.time()})
            r_conn.hset(self.active_user_info_key, user_id, pos_str)

            if info.get('line_id'):
                if manual == 1 or r_conn.llen(key) >= 20:
                    datas = r_conn.lrange(key, 0, -1)
                    r_conn.ltrim(key, 1000, 1000)

                    with CursorManager() as cursor:
                        pos_infos = []
                        for data in datas:
                            data = json.loads(data)
                            pos_infos.append((data.get('user_id'), data.get('latitude'), data.get('longitude'), data.get('manual'), data.get('create_time')))
                        pos_infos.append((user_id, latitude, longitude, manual, time.time()))
                        self._new_records(cursor, ['user_id', 'latitude', 'longitude', 'manual', 'create_time'], pos_infos)
                else:
                    r_conn.rpush(key, pos_str)

    def query_records(self, user_id, max_id=None, start=None, end=None, **kwargs):
        result = None
        if r_conn.hexists(self.active_user_info_key, user_id):
            result = []
            with CursorManager() as cursor:
                if kwargs:
                    val = [(kv[0] + '="' + str(kv[1]) + '"') for kv in kwargs.items()]
                else:
                    val = ['1=1']
                val.append('user_id=%d' % user_id)
                if max_id is not None:
                    val.append('id>%d' % max_id)
                if start is not None:
                    val.append('create_time>=%d' % int(start))
                if end is not None:
                    val.append('create_time<=%d' % int(end))

                try:
                    sql_str = '''
                        SELECT id, latitude, longitude, create_time, manual FROM %s WHERE %s order by create_time asc
                    ''' % (self._table, ' and '.join(val))
                    print(sql_str)
                    cursor.execute(sql_str)
                    result = cursor.fetchall()
                except Exception as e:
                    print(e)
        return result

class ExamCalculate(object):
    pi = 3.14159265358979324
    a = 6378245.0
    ee = 0.00669342162296594323

    @classmethod
    def _transform_lat(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * ExamCalculate.pi) + 20.0 * math.sin(2.0 * x * ExamCalculate.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * ExamCalculate.pi) + 40.0 * math.sin(y / 3.0 * ExamCalculate.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * ExamCalculate.pi) + 320 * math.sin(y * ExamCalculate.pi / 30.0)) * 2.0 / 3.0

        return ret

    @classmethod
    def _transform_lon(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * ExamCalculate.pi) + 20.0 * math.sin(2.0 * x * ExamCalculate.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * ExamCalculate.pi) + 40.0 * math.sin(x / 3.0 * ExamCalculate.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * ExamCalculate.pi) + 300.0 * math.sin(x / 30.0 * ExamCalculate.pi)) * 2.0 / 3.0

        return ret

    @classmethod
    def gps_to_amap(self, latitude, longitude):
        if longitude >= 72.004 and longitude <= 137.8347 and latitude >= 0.8293 and latitude <= 55.8271:
            d_lat = self._transform_lat(longitude - 105.0, latitude - 35.0)
            d_lon = self._transform_lon(longitude - 105.0, latitude - 35.0)
            rad_lat = latitude / 180.0 * ExamCalculate.pi
            magic = math.sin(rad_lat)
            magic = 1 - ExamCalculate.ee * magic * magic
            sqrt_magic = math.sqrt(magic);
            d_lat = (d_lat * 180.0) / ((ExamCalculate.a * (1 - ExamCalculate.ee)) / (magic * sqrt_magic) * ExamCalculate.pi)
            d_lon = (d_lon * 180.0) / (ExamCalculate.a / sqrt_magic * math.cos(rad_lat) * ExamCalculate.pi)

            latitude = latitude + d_lat
            longitude = longitude + d_lon

        return latitude, longitude

    @classmethod
    def dd2k_to_amap(self, x, y):
        a = 6378137.0
        ee = math.sqrt(0.0066943802290)
        b = math.sqrt(a * a * (1 - ee * ee))
        c = a * a / b
        epp = math.sqrt((a * a - b * b) / b / b)

        num = int(str(y)[:2])
        y = float(str(y)[2:-1]) - 500000

        midlong = (6 * num - 3) * 3.1415926535898 / 180

        b = math.sqrt(a * a * (1 - ee * ee))
        c = a * a / b
        epp = math.sqrt(a * a - b * b) / b

        m0 = a * (1 - ee * ee)
        m2 = 3.0 / 2.0 * m0 * ee * ee
        m4 = 5.0 / 4.0 * ee * ee * m2
        m6 = 7.0 / 6.0 * ee * ee * m4
        m8 = 9.0 / 8.0 * ee * ee * m6
        a0 = m0 + m2 / 2.0 + 3.0 / 8.0 * m4 + 5.0 / 16.0 * m6 + 35.0 / 128.0 * m8
        a2 = m2 / 2 + m4 / 2 + 15.0 / 32.0 * m6 + 7.0 / 16.0 * m8
        a4 = m4 / 8.0 + 3.0 / 16.0 * m6 + 7.0 / 32.0 * m8
        a6 = m6 / 32.0 + m8 / 16.0
        a8 = m8 / 128.0

        Bf = x / a0
        B = 0.0

        while (math.fabs(Bf - B) > 1E-10) :
            B = Bf
            sb = math.sin(B)
            cb = math.cos(B)
            s2b = sb * cb * 2
            s4b = s2b * (1 - 2 * sb * sb) * 2
            s6b = s2b * math.sqrt(1 - s4b * s4b) + s4b * math.sqrt(1 - s2b * s2b)
            Bf = (x - (-a2 / 2.0 * s2b + a4 / 4.0 * s4b - a6 / 6.0 * s6b)) / a0

        itaf = epp * math.cos(Bf)
        tf = math.tan(Bf)
        Vf = math.sqrt(1 + epp * epp * math.cos(Bf) * math.cos(Bf))
        Nf = c / Vf

        ynf = y / Nf

        latitude = Bf - 1.0 / 2.0 * Vf * Vf * tf * (ynf * ynf - 1.0 / 12.0 * math.pow(ynf, 4) * (5 + 3 * tf * tf +
                            itaf * itaf - 9 * math.pow(itaf * tf, 2)) +
                            1.0 / 360.0 * (61 + 90 * tf * tf + 45 * math.pow(tf, 4)) * math.pow(ynf, 6))

        longitude = (ynf / math.cos(Bf) - (1 + 2 * tf * tf + itaf * itaf) * math.pow(ynf, 3) / 6.0 / math.cos(Bf) +
                              (5 + 28 * tf * tf + 24 * math.pow(tf, 4) + 6 * itaf * itaf + 8 * math.pow(itaf * tf, 2)) *
                              math.pow(ynf, 5) / 120.0 / math.cos(Bf)) + midlong

        return self.gps_to_amap(latitude * 180 / math.pi, longitude * 180 / math.pi)

    @classmethod
    def _time_to_timestamp(self, time_str):
        try:
            time_info = time_str.split(':')
            return int(time_info[0]) * 3600 + int(time_info[1]) * 60
        except Exception as e:
            print(e)
        return -1

    @classmethod
    def _conver_line_info(self, line_info):
        line_data = {'name': line_info.get('name')}

        points = []
        for point in json.loads(line_info.get('points')):
            x = float(point.get('x'))
            y = float(point.get('y'))
            lat, lon = self.dd2k_to_amap(x, y)
            stime = self._time_to_timestamp(point.get('stime'))
            etime = self._time_to_timestamp(point.get('etime'))
            point.update({
                'latitude': lat,
                'longitude': lon,
                'x': x,
                'y': y,
                'stime': stime,
                'etime': etime,
                'locations': []
            })
            points.append(point)
        line_data.update({'points': points})

        return line_data

    @classmethod
    def _prepare_data(self, user_id, active_id):
        line_info = None
        position_info = None

        with CursorManager() as cursor:
            user_info = table_manager(ExamUser).query_records(cursor, id=user_id, exam_id=active_id)
            if user_info:
                user_info = user_info[0]
                line_info = table_manager(ExamLine).query_record(cursor, id=user_info.get('line_id'))
                if line_info:
                    position_info = table_manager(UserRecord, str(active_id)).query_records(user_id, manual=1)

        return self._conver_line_info(line_info), position_info

    @classmethod
    def _calculate_distance(self, s_latitude, s_longitude, e_latitude, e_longitude):
        d1 = 0.01745329251994329
        d2 = s_longitude * d1
        d3 = s_latitude * d1
        d4 = e_longitude * d1
        d5 = e_latitude * d1

        d6 = math.sin(d2)
        d7 = math.sin(d3)
        d8 = math.cos(d2)
        d9 = math.cos(d3)
        d10 = math.sin(d4)
        d11 = math.sin(d5)
        d12 = math.cos(d4)
        d13 = math.cos(d5)

        diff1 = d9 * d8 - d13 * d12
        diff2 = d9 * d6 - d13 * d10
        diff3 = d7 - d11
        d14 = math.sqrt(diff1 * diff1 + diff2 * diff2 + diff3 * diff3)

        return (math.asin(d14 / 2.0) * 12742001.579854401)

    @classmethod
    def _dispatch_nearest_point(self, points, record):
        min_distance = 100000000
        min_index = 0
        for index, point in enumerate(points):
            distance = self._calculate_distance(record.get('latitude'), record.get('longitude'), point.get('latitude'), point.get('longitude'))
            if distance < min_distance:
                min_index = index
                min_distance = distance

        record.update({'distance': min_distance})
        points[min_index].get('locations').append(record) 

    @classmethod
    def calculate(self, user_id):
        active_id = table_manager(Exam).get_active_id()
        if active_id <= 0:
            return {}

        line_info, records = self._prepare_data(user_id, active_id)

        for record in records:
            self._dispatch_nearest_point(line_info.get('points'), record)

        result = {'line_name': line_info.get('line_name')}

        size = 0
        for point in line_info.get('points'):
            if point.get('stime') > 0 and point.get('etime') > 0:
                size += 2
            else:
                size += 1
        weight = 10.0 / size

        points = []
        total_score = 0
        for index, point in enumerate(line_info.get('points')):
            suite_location = None
            min_distance = 1000000
            stime = point.get('stime')
            etime = point.get('etime')
            for location in point.get('locations'):
                record_time = location.get('create_time') % 86400
                if location.get('distance') < min_distance and ((stime >= 0 and record_time >= stime and record_time <= etime) or stime <= 0):
                    suite_location = location
                    min_distance = location.get('distance')

            w = 2 * weight if stime >= 0 else 1 * weight

            if suite_location:    
                score = 0
                if min_distance < point.get('level1'):
                    score = 100
                elif min_distance < point.get('level2'):
                    score = 80
                elif min_distance < point.get('level3'):
                    score = 60
                score = score * w

                data = {
                    'id': index + 1,
                    'latitude': suite_location.get('latitude'),
                    'longitude': suite_location.get('longitude'),
                    'weight': w,
                    'distance': min_distance,
                    'score': w * score
                }
                total_score += score
            else:
                data = {
                    'id': index + 1,
                    'latitude': -1,
                    'longitude': -1,
                    'weight': w,
                    'distance': -1,
                    'score': 0
                }
            points.append(data)

        result.update({'points': points, 'total_score': total_score})
        
        return result

    @classmethod
    def calculate_all(self, level1, level2, level3, level4):
        result = {}

        active_id = table_manager(Exam).get_active_id()
        if active_id <= 0:
            return result

        
        with CursorManager() as cursor:
            exam_info, _ = table_manager(Exam).query_record(cursor, id=active_id)
            if not exam_info:
                return result

            # level1, level2, level3, level4, score1, score2, score3, score4 = (
            #     float(exam_info.get('level1')), float(exam_info.get('level2')),
            #     float(exam_info.get('level3')), float(exam_info.get('level4')), 
            #     float(exam_info.get('score1')), float(exam_info.get('score2')),
            #     float(exam_info.get('score3')), float(exam_info.get('score4')), 
            # )
            table_manager(Exam).update_record(cursor, active_id, level1=level1, level2=level2, level3=level3, level4=level4)

            score1, score2, score3, score4 = (
                float(exam_info.get('score1')), float(exam_info.get('score2')),
                float(exam_info.get('score3')), float(exam_info.get('score4')),
            )
            result = {'examname': exam_info.get('name'), 'level1': level1, 'level2': level2, 'level3': level3, 'level4': level4}
            users = []

            user_info_list = table_manager(ExamUser).query_records(cursor, exam_id=active_id, line_id=None)
            for user_info in user_info_list:
                line_id = user_info.get('line_id')

                line_info = table_manager(ExamLine).query_record(cursor, id=line_id)
                
                if not line_info or not line_info.get('points'):
                    continue

                line_info = self._conver_line_info(line_info)
                records = table_manager(UserRecord, str(active_id)).query_records(user_info.get('id'), manual=1)
                if records is None:
                    continue

                # >>>>>>>>
                for record in records:
                    self._dispatch_nearest_point(line_info.get('points'), record)

                user_result = {'linename': line_info.get('name'), 'username': user_info.get('username'), 'departname': user_info.get('departname')}

                points = []
                total_score = 0
                for index, point in enumerate(line_info.get('points')):
                    suite_location = None
                    min_distance = 1000000
                    stime = point.get('stime')
                    etime = point.get('etime')
                    for location in point.get('locations'):
                        record_time = location.get('create_time') % 86400
                        if location.get('distance') < min_distance and ((stime >= 0 and record_time >= stime and record_time <= etime) or stime <= 0):
                            suite_location = location
                            min_distance = location.get('distance')

                    w = float(point.get('weight'))
                    if suite_location:
                        score = 0
                        if min_distance <= level1:
                            score = score1
                        elif min_distance <= level2:
                            score = score2
                        elif min_distance <= level3:
                            score = score3
                        elif min_distance <= level4:
                            score = score4

                        data = {
                            'id': index + 1,
                            'latitude': suite_location.get('latitude'),
                            'longitude': suite_location.get('longitude'),
                            'weight': w,
                            'distance': min_distance,
                            'score': score
                        }
                        total_score += (score * w)
                    else:
                        data = {
                            'id': index + 1,
                            'latitude': -1,
                            'longitude': -1,
                            'weight': w,
                            'distance': -1,
                            'score': 0
                        }
                    points.append(data)

                user_result.update({'points': points, 'total_score': total_score})
                table_manager(ExamUser).update_record(cursor, user_info.get('id'), exam_id=user_info.get('exam_id'), detail=json.dumps(user_result))
                users.append(user_result)
            result.update({'users': users})
        print(result)
        return result


_table_map = dict()
def table_manager(table, ext_name=None, create=True, **kwargs):
    global _table_map

    table_name = str(table).split('.')[-1]
    table_name = table_name + '_' + ext_name if ext_name else table_name

    if not _table_map.get(table_name) and create:
        obj = table(ext_name) if ext_name else table()
        _table_map.update({table_name: obj})
    return _table_map.get(table_name)

# print(ExamCalculate._calculate_distance(39.923423, 116.368904, 39.922501, 116.387271))
# ExamCalculate.calculate(2)        
# print(ExamCalculate.dd2k_to_amap(4425446.67386214, 20453185.9322068))
# ExamCalculate.calculate_all(2, 10, 15, 30)

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

################################ FOR GPS Device ##############################################################

def add_device_record(device_id, latitude=None, longitude=None, ischeckin=False):
    if not device_id:
        return

    exam = table_manager(Exam)
    active_id = exam.get_active_id()
    if active_id < 0:
        return

    with CursorManager() as cursor:
        exam_user = table_manager(ExamUser)
        users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)
        if not users:
            exam_user.new_record(cursor, {
                'exam_id': active_id,
                # 'line_id': None,
                'device_id': device_id,
                'username': '',
                'departname': ''
            })

            users = exam_user.query_records(cursor, device_id=device_id, exam_id=active_id)

            if not users:
                return

        user = users[0]

        if latitude and longitude:
            user_record = table_manager(UserRecord, str(active_id), False)
            if user_record:
                user_record.add_record(user.get('id'), latitude, longitude, 1 if ischeckin else 2)

