#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# create ramdisk on macOS with APFS
# https://stackoverflow.com/questions/46224103/create-apfs-ram-disk-on-macos-high-sierra
# hdid -nomount ram://<blocksize>
# <blocksize> is 2048 * desired size in megabytes
#
# one liner:
#    diskutil partitionDisk $(hdiutil attach -nomount ram://2048000) 1 GPTFormat APFS 'ramdisk' '100%'


from __future__ import print_function
import multiprocessing as mp
import time
import signal
# fix path for now
import sys
sys.path.append("../../")

from pygecko.transport import Pub, Sub
from pygecko.transport.zmqclass import SubNB
from pygecko.transport import zmqTCP, GeckoCore
from math import sin, cos, pi, sqrt

import cv2

import numpy as np

# Holly crap namespace and pickle use a lot of cpu!
# zmq hs only 23%, but syncmanager is 77%
# ns == msg image True
# +------------------------------
# | Alive processes: 11
# +------------------------------
# | subscribe[19339].............. cpu: 12.2%    mem: 0.10%
# | subscribe[19343].............. cpu: 13.7%    mem: 0.10%
# | SyncManager-1[19327].......... cpu: 77.4%    mem: 0.19%
# | subscribe[19338].............. cpu: 12.5%    mem: 0.10%
# | subscribe[19341].............. cpu: 13.6%    mem: 0.10%
# | publish[19336]................ cpu: 8.7%    mem: 0.40%
# | GeckoCore[19328].............. cpu: 23.3%    mem: 0.11%
# | subscribe[19344].............. cpu: 13.8%    mem: 0.10%
# | subscribe[19342].............. cpu: 13.7%    mem: 0.11%
# | publish[19337]................ cpu: 8.8%    mem: 0.40%
# | subscribe[19340].............. cpu: 13.7%    mem: 0.10%
# if 'b' in msg:
#     print('ns == msg image', ns.image == msg['b'])

def chew_up_cpu():
    # chew up some cpu
    for i in range(90):
        m = sin(i*pi/180)*cos(i*pi/180)*sin(i*pi/180)*cos(i*pi/180)*sin(i*pi/180)*cos(i*pi/180)
        sqrt(m**9)


class GeckoRate(object):
    def __init__(self, hertz):
        self.last_time = time.time()
        self.dt = 1/hertz

    def sleep(self):
        """
        This uses sleep to delay the function. If your loop is faster than your
        desired Hertz, then this will calculate the time difference so sleep
        keeps you close to you desired hertz. If your loop takes longer than
        your desired hertz, then it doesn't sleep.
        """
        now = time.time()
        diff = now - self.last_time
        # new_sleep = diff if diff < self.dt else 0
        if diff < self.dt:
            new_sleep = self.dt - diff
        else:
            new_sleep = 0

        self.last_time = now

        time.sleep(new_sleep)

class GeckoPy(object):
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self._kill = False
        self.subs = []

    def is_shutdown(self):
        return self._kill

    def Rate(self, hertz):
        return GeckoRate(hertz)

    def get_time(self):
        return time.time()

    def Publisher(self, uds_file=None, host='localhost', queue_size=10):

        p = Pub()

        if uds_file:
            raise Exception()
        else:
            addr = zmqTCP(host, 9998)

        p.connect(addr, queue_size=queue_size)
        return p

    def Subscriber(self, topics, cb, host='localhost', uds_file=None):
        s = SubNB(cb, topics=topics)

        if uds_file:
            raise Exception()
        else:
            addr = zmqTCP(host, 9999)

        s.connect(addr)
        self.subs.append(s)

    def signal_handler(self, signalnum, stackframe):
        self._kill = True
        # print('ignore ctrl-c signal:', signalnum)
        print('GeckoPy got ctrl-c:', signalnum)
        print('kill =', self._kill)

    def spin(self, hertz=100):
        rate = self.Rate(1.2*hertz)
        while not self._kill:
            for sub in self.subs:
                sub.recv()
            rate.sleep()


# def gecko_setup():
#     # kill -l
#     # signal.signal(signal.SIGINT, signal_handler)
#     # signal.signal(signal.SIGTERM, signal_handler)
#     def signal_handler(signalnum, stackframe):
#         # print('ignore ctrl-c signal:', signalnum)
#         pass
#     signal.signal(signal.SIGINT, signal_handler)


def publish(**kwargs):
    geckopy = GeckoPy()
    rate = geckopy.Rate(20)

    topic = kwargs.get('topic', 'test')

    p = geckopy.Publisher()

    cnt = 0
    # raw_img = np.random.rand(640, 480)  # HD (1920x1080) kills performance
    raw_img = np.random.rand(1,5)
    while not geckopy.is_shutdown():
        img = raw_img.tobytes()
        msg = {'a': cnt, 'b': img, 's': time.time()}
        p.pub(topic, msg)  # topic msg
        cnt += 1
        # print('>> published msg on topic {}'.format(topic))

        # chew up some cpu
        # chew_up_cpu()

        # sleep
        rate.sleep()

    print('pub bye ...')


def pcv(**kwargs):
    geckopy = GeckoPy()
    rate = geckopy.Rate(30)

    topic = kwargs.get('topic', 'test')

    p = geckopy.Publisher()

    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 480)

    while not geckopy.is_shutdown():
        ok, img = camera.read()
        if ok:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = img.tobytes()
            msg = {'img': img, 's': time.time()}
            p.pub(topic, msg)  # topic msg

        # sleep
        rate.sleep()

    camera.release()
    # time.sleep(1)
    print('cv bye ...')

# def subscribe(**kwargs):
#     # if kwargs.get('signal', False):
#     #     gecko_setup()
#     geckopy = GeckoPy()
#
#     topic = kwargs.get('topic', 'test')
#     s = Sub(topics=[topic])
#     addr = zmqTCP('localhost', 9999)
#     s.connect(addr)
#     # s = geckopy.Subscriber([topic])
#
#     while not geckopy.is_shutdown():
#         # print('loop')
#         # print(s.recv(flags=zmq.NOBLOCK))
#         t, msg = s.recv()
#         # print("<< recv[{}][{}]: {}".format(t, msg['a'], time.time() - msg['s']))
#         # chew up some cpu
#         chew_up_cpu()
#         chew_up_cpu()
#         chew_up_cpu()
#         chew_up_cpu()
#
#     print('sub bye ...')


def subscribe2(**kwargs):
    geckopy = GeckoPy()

    def f(t, m):
        # print('>> Message[{}]'.format(t))
        chew_up_cpu()
        chew_up_cpu()
        chew_up_cpu()
        chew_up_cpu()
        pass

    topic = kwargs.get('topic', 'test')
    # s = SubNB(f, topics=[topic])
    # addr = zmqTCP('localhost', 9999)
    # s.connect(addr)
    s = geckopy.Subscriber([topic], f)
    geckopy.spin(20)


if __name__ == "__main__":
    kw = {'topic': 'hello'}
    # publish(kwargs=kw)
    subscribe2(kwargs=kw)
