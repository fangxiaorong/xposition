#!/usr/bin/python
#coding:utf-8

import click

from tcpserver.server import GPSServer
from tornado.ioloop  import IOLoop

@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--port', type=int, default=8001, help='service port')
def location(port):
    """Command for start location server"""
    print("Server start ......")
    server = GPSServer()  
    server.listen(port)  
    IOLoop.instance().start()

@click.group()
def cli2():
    pass

@cli2.command()
@click.option('--port', type=int, default=8002, help='service port')
def protal(port):
    """Command for start protal server"""
    print(port)

cli = click.CommandCollection(sources=[cli1, cli2])

if __name__ == '__main__':
    cli()
