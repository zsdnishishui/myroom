#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Michael Liao'

import time, uuid

from orm import Model, StringField, IntegerField

class User(object):
    pass

class Light(Model):
    __table__ = 'light'

    id = IntegerField(primary_key=True)
    state = StringField(ddl='varchar(50)')
    add_time = IntegerField()

class TempHum(Model):
    __table__ = 'temp_hum'

    id = IntegerField(primary_key=True)
    temp = IntegerField()
    humidity = IntegerField()
