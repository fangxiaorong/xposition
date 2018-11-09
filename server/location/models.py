#!/usr/bin/python
#coding:utf-8


from orm import Model, DynamicModel, StringField, BooleanField, FloatField, TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class ExamModel(Model):
    __table__ = 'exam'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    file = StringField(ddl='varchar(250)')
    remark = TextField()

    def test(self):
        print('xyz---------')
        

class UserModel(DynamicModel):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
