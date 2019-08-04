#!/usr/bin/python
#coding:utf-8

import click

from tcpserver.server import GPSServer, TestServer
from tornado.ioloop  import IOLoop

from backends.server import app

@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--port', type=int, default=8001, help='service port')
def location(port):
    """Command for start location server"""
    print("Server start ......")
    server = GPSServer()
    server.listen(port) # simple single-process
    # server.bind(port)
    # server.start(0)
    IOLoop.instance().start()

@click.group()
def cli2():
    pass

@cli2.command()
@click.option('--port', type=int, default=8002, help='service port')
def protal(port):
    """Command for start protal server"""
    print("Server start ......")
    app.listen(port)
    IOLoop.instance().start()


@click.group()
def cli3():
    pass

@cli3.command()
@click.option('--port', type=int, default=8003, help='service port')
def xlocation(port):
    """Command for start location server"""
    print("Server start ......")
    server = TestServer()
    server.listen(port) # simple single-process
    IOLoop.instance().start()

cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()
    # from backends import test
    # test()

    # from location.models import ExamModel

    # x = ExamModel()
    # ExamModel.create_table()

