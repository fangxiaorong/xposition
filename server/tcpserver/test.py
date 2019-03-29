from tornado.tcpserver import TCPServer
from tornado.tcpclient import TCPClient
from tornado.ioloop import IOLoop
from tornado import gen
import time

class Connection(object):

    @gen.coroutine
    def _resolve(self, idefy, stream):
        d = yield stream.read_bytes(1)
        time.sleep(0.1)
        print(idefy, d)

    @gen.coroutine
    def handler(self, stream, address):
        idefy = yield stream.read_bytes(1)
        print(idefy, 'init')
        # time.sleep(1)
        # yield stream.read_bytes(1)
        # time.sleep(1)
        # print(idefy, 'sleep end')
        # data = yield stream.read_bytes(2)
        # print(idefy, data)
        for x in range(9):
            yield self._resolve(idefy, stream)
        print(idefy, 'end')
        
class Conn(object):
    def __init__(self, stream, address):
        super(Conn, self).__init__()
        self.is_running = False
        self._stream = stream
        self._address = address

    def handler(self):
        print('start::::', self._address)
        
        self._stream.read_until(b'\r\n', self._read_loop, 1024)
        self._write_loop('y')

    def _read_loop(self, data):
        print(self._address, ':read:', data)

        self._stream.read_until(b'\r\n', self._read_loop, 1024)

    def _write_loop(self, data):
        IOLoop.current().call_later(3, self._write_loop, data + 'x')
        if data != 'y':
            print(self._address, ':write:', data)


class Server(TCPServer):
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

    # @gen.coroutine
    # def handle_stream(self, stream, address):
    #     # yield Connection().handler(stream, address)

    #     idefy = stream.read_bytes(1)
    #     while idefy.running():
    #         time.sleep(0.01)
    #     print(idefy.result(), 'init')
    #     for x in range(9):
    #         d = stream.read_bytes(1)
    #         while d.running():
    #             time.sleep(0.01)
    #         time.sleep(0.1)
    #         print(idefy.result(), d.result())
    #     print(idefy.result(), 'end')

    def handle_stream(self, stream, address):
        Conn(stream, address).handler()

def start_server():
    server = Server()
    # server.listen(8036) # simple single-process
    server.bind(8036)
    server.start(0)
    IOLoop.instance().start()


@gen.coroutine
def start_client():
    streams = []
    for d in [b'abcdefgeh\r\nlajdkjlsdf\r\n', b'LDFKJGLKAJ\r\nDFJLSDAF\r\n']:
        stream = yield TCPClient().connect( 'localhost', 8036)
        streams.append(stream)
        yield stream.write(d)

    time.sleep(5)

    idx = 0
    for stream in streams:
        idx += 1
        yield stream.write(b'%d:xxx\r\n%d:xxx\r\n' % (idx, idx))

@gen.coroutine
def start_test():
    stream = yield TCPClient().connect('localhost', 8001)
    yield stream.write(b'xx\x11\x01\x08gYp\x11\x96u\x90\x10\x1c2\x01\x00\x01\x88\xf5\r\n')
    yield stream.write(b'xx\x19\x10\x13\x03\x1c\x11\t\r\xc8\x04K\xb3\x1b\x0c}Pz\x00\x14\x00\x00\x01\x00\x16\xb2\xa4\r\n')
    # yield stream.write(b'xx\x11\x01\x08gYp\x11\x96u\x90\x10\x1c2\x01\x00\x01\x88\xf5\r\n')
    # yield stream.write(b'xx\n\x13\x08\x06\x02\x00\x01\x00\x02-/\r\n')
    # yield stream.write(b'xx\r\x1f\x00\x00\x00\x00\x00\x00\x00\x01\x00\x03\xef_\r\n')
    # yield stream.write(b'xx\x1f\x81\x17\x00\x00\x00\x00SEEFN&&&&&&&&&&&&##\x00\x01\x00\x04c\xfc\r\n')
    # yield stream.write(b'xx!\x81\x19\x00\x00\x00\x00SEESOS:18851118840,,#\x00\x01\x00\x05@N\r\n')
    # yield stream.write(b'xx0\x81(\x00\x00\x00\x00SEETIME:0|0||||||||]|||||||]|||||||}\x00\x01\x00\x06.n\r\n')
    # yield stream.write(b'xx0\x81(\x00\x00\x00\x00SEETIME:1|1||||||||]|||||||]|||||||}\x00\x01\x00\x07hv\r\n')
    # yield stream.write(b'xx\r\x8b\x01\xcc\x00\x11A\x00Q\xd7\x00\x08\x1e\xa6\r\n')
    # time.sleep(5)
    # yield stream.write(b'xx\x99\x81\x93\x00\x00\x00\x00CTRLPARAMS:GTIMER=0;TIMER=0,30;PWRLIMIT=0;RING=1;CALLMODE=2;SIMALM=0,0;BATALM=1,0;PWRONALM=1,0;PWROFFALM=1,0;BLINDALM=0,60,20,1;SOSALM=1,3#\x00\x00\x00\x02\x00\tL\xbd\r\n')
    # yield stream.write(b"xx-\x81'\x00\x00\x00\x00ALLGFENCES:1,0;2,0;3,0;4,0;5,0#\x00\x00\x00\x02\x00\n\xae\x07\r\n")
    # yield stream.write(b'xx\x1c\x81\x16\x00\x00\x00\x00W\x00H\x00I\x00T\x00E\x00:\x00#\x00\x00\x00\x00\x01\x00\x0bK8\r\n')
    # yield stream.write(b'xx\x1e\x81\x18\x00\x00\x00\x00OK#AL#: No data!\x00\x00\x00\x02\x00\x0cc\xa5\r\n')
    # yield stream.write(b'xxO,\x13\x03\x1b\x01\x03\x0f\x01\xcc\x00\x11A\x00Q\xd7S\x11A\x00\x05+P\x11A\x00[\x9b[\x11A\x00H\xbfa\x11A\x00Z\xd6a\x11A\x00\x83\xc2a\x11A\x00\xd4\xfdc\xff\x03\\\xc9\x99\xa3W\x80$\\\xc9\x99\xa3S\xf1$$\xa2\xe1\xf0\xe9\xf24\x00\x0etn\r\n')

if __name__ == '__main__':
    # start_server()
    # IOLoop.current().run_sync(start_client)
    IOLoop.current().run_sync(start_test)

