from __future__ import print_function
import time
import os
import time
from math import pi

from pygecko.multiprocessing import geckopy
from pygecko.transport import Pub, Sub
from pygecko.transport import zmqTCP, zmqUDS
from pygecko.transport import GeckoCore
from pygecko.multiprocessing import GeckoSimpleProcess

from pygecko import FileJson, FileYaml
from pygecko import Quaternion
from pygecko import Vector
from pygecko import IMU
from pygecko import Twist
# from pygecko import Wrench
from pygecko import Pose
# from pygecko import Joystick
from pygecko import Image, image2msg, msg2image
# from pygecko import PoseStamped
# from pygecko import Lidar

# Fake cv2 things for testing
import pygecko.fake.fake_camera as pcv2


def test_images():
    img = pcv2.cvImage(6, 4)
    msg = image2msg(img)
    print(msg)
    ret = msg2image(msg)
    print(ret)
    assert img.all() == ret.all()


def test_compressed_images():
    img = pcv2.cvImage(6, 4)
    msg = image2msg(img, compressed=True)
    print(msg)
    ret = msg2image(msg)
    print(ret)
    assert img.all() == ret.all()



def file_func(Obj, fname):
    data = {'a':1, 'bob':[1,2,3,4], 'c':"hello cowboy", 'd': {'a':pi}}
    f = Obj()
    f.set(data)
    f.write(fname)
    d = f.read(fname)
    assert d == data
    os.remove(fname)


def test_json():
    file_func(FileJson, 'test.json')


def test_yaml():
    file_func(FileYaml, 'test.yml')


def test_rate():
    rate = geckopy.Rate(10)
    start = time.time()
    for _ in range(10):
        rate.sleep()
    stop = time.time()
    # print(stop - start)
    assert (stop - start) + 0.05 > 1.0


# # tcp setup
# tcp_pub = zmqTCP('localhost', 9998)
# tcp_sub = zmqTCP('localhost', 9999)
#
# # unix domain setup
# uds_ifile = zmqUDS('/tmp/uds_ifile')
# uds_ofile = zmqUDS('/tmp/uds_ofile')


def msg_zmq():
    # start message hub
    core = GeckoCore()
    core.start()

    msg1 = IMU(
        Vector(1,2,3),
        Vector(11,12,13),
        Vector(21,22,23))

    msg2 = Twist(
        Vector(1,2,3),
        Vector(11,12,13))

    msg3 = Pose(
        Vector(1,2,3),
        Quaternion(1,2,3,4))

    def publisher(**kwargs):
        geckopy.init_node(**kwargs)
        p = geckopy.Publisher(topics=['test'])
        time.sleep(1)  # need this!!

        for msg in [msg1,msg2,msg3]:
            p.pub('test', msg)
            time.sleep(0.01)

    args = {'host': 'localhost'}
    p = GeckoSimpleProcess()
    p.start(func=publisher, name='publisher', kwargs=args)

    # subscriber
    s = Sub(topics=['test'])
    s.connect(sub_addr)

    for msg in [msg1,msg2,msg3]:
        t, m = s.recv()
        assert t == b'test'  # FIXME: fix stupid binary string crap!
        assert msg == m

    core.join(0.1)
    time.sleep(1)  # if I run these too fast, I get errors on bind()


# def test_msg_zmq_uds():
#     msg_zmq(uds_ifile, uds_ofile)


def test_msg_zmq_tcp():
    msg_zmq()


def py_zmq():
    # start message hub
    core = GeckoCore()
    core.start()

    def publisher(**kwargs):
        geckopy.init_node(**kwargs)
        p = geckopy.Publisher(topics=['test'])
        time.sleep(1)
        msg = {'a':1, 'b':[1,2,3], 'c':'hello cowboy'}
        p.pub('test', msg)  # topic msg

    args = {'host': "localhost"}
    p = GeckoSimpleProcess()
    p.start(func=publisher, name='publisher', kwargs=args)

    # subscriber
    s = Sub(topics=['test'])
    s.connect(sub_addr)
    t, msg = s.recv()

    assert t == b'test'
    assert msg == {'a':1, 'b':[1,2,3], 'c':'hello cowboy'}

    core.join(0.1)
    time.sleep(1)  # if I run these too fast, I get errors on bind()


def test_py_zmq_tcp():
    py_zmq()


# def test_py_zmq_uds():
#     py_zmq(uds_ifile, uds_ofile)


# def py_geckpy(pub_addr, sub_addr):
#     # start message hub
#     core = GeckoCore(pub_addr, sub_addr)
#     core.start()
#
#     geckopy = GeckoPy()
#
#     def callback(t, msg):
#         assert t == b'test'
#         assert msg == {'a':1, 'b':[1,2,3], 'c':'hello cowboy'}
#
#     def callback(**kwargs):
#         addr = kwargs.get('addr')
#         p = Pub()
#         p.connect(addr)
#         time.sleep(1)
#         msg = {'a':1, 'b':[1,2,3], 'c':'hello cowboy'}
#         p.pub('test', msg)  # topic msg
#
#
#
#     args = {'addr': pub_addr}
#     p = GeckoSimpleProcess()
#     p.start(func=publisher, name='publisher', kwargs=args)
#
#     # subscriber
#     s = Sub(topics=['test'])
#     s.connect(sub_addr)
#     t, msg = s.recv()
#
#     print(t, msg)
#
#     assert t == b'test'
#     assert msg == {'a':1, 'b':[1,2,3], 'c':'hello cowboy'}
#
#     p.join(0.1)
#     core.join(0.1)
#
# def test_py_geckopy_tcp():
#     py_geckpy(tcp_pub, tcp_sub)
#
#
# def test_py_geckopy_uds():
#     py_geckpy(uds_ifile, uds_ofile)
