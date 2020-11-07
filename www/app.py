#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
async web application.
'''

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web 
import orm
from coroweb import add_routes, add_static
from handlers import start_sch,init_deng_state,init_chuang_state,cookie2user
COOKIE_NAME = 'awesession'

async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        # await asyncio.sleep(0.3)
        return (await handler(request))
    return logger

async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))
    return parse_data

async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response
async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.url, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user['id'])
                request.__user__ = user
        if not str(request.url).startswith('http://raspberrypi') and request.path!="/api/login" and request.path.startswith('/api/') and request.__user__ is None:
            return web.HTTPFound('/signin')
        return (await handler(request))
    return auth

async def init(loop):
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='123456', db='myroom')
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory,auth_factory
    ])
    add_routes(app, 'handlers') #添加接口路径
    add_static(app) #添加静态路径
    start_sch() #启动定时框架
    init_deng_state() #初始化灯的状态
#    init_chuang_state() #初始化窗帘的状态
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 9000)
    logging.info('server started')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()