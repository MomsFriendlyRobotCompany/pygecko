# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# ##############################################
# # The MIT License (MIT)
# # Copyright (c) 2018 Kevin Walchko
# # see LICENSE for full details
# ##############################################
#
# # from pygecko.transport import Pub, Sub
# from pygecko.transport import GeckoCore
# from pygecko.transport import zmqUDS
# from pygecko.multiprocessing import geckopy
# from pygecko.test import GeckoSimpleProcess
# import time
#
#
# def publish(**kwargs):
#     geckopy.init_node(**kwargs)
#     rate = geckopy.Rate(2)
#
#     print('pub', kwargs)
#
#     topic = kwargs.get('topic', 'test')
#     addr = kwargs.get('pub_uds', None)
#     print('publish addr:', addr)
#
#     p = geckopy.Publisher(addr=addr)
#
#     while not geckopy.is_shutdown():
#         msg = {'s': time.time()}
#         p.pub(topic, msg)  # topic msg
#
#         rate.sleep()
#
#     geckopy.log('pub bye ...')
#
#
# def subscribe(**kwargs):
#     geckopy.init_node(**kwargs)
#
#     def f(t, m):
#         geckopy.log('>> Message[{}]'.format(t))
#
#     topic = kwargs.get('topic', 'test')
#     addr = kwargs.get('sub_uds', None)
#     print('subscriber addr:', addr)
#
#     geckopy.Subscriber([topic], f, addr=addr)
#     geckopy.spin(20)
#     geckopy.log('sub bye ...')
#
#
# if __name__ == '__main__':
#     # info to pass to processes
#     args = {
#         'topic': 'hi'
#     }
#
#     args['geckocore'] = {
#         'in_addr': zmqUDS('/tmp/uds_ifile'),
#         'out_addr': zmqUDS('/tmp/uds_ofile')
#     }
#     # this is sort of like crossing RX/TX lines here
#     #        +---------+
#     # pub -> | in  out | -> sub
#     #        +---------+
#     core = GeckoCore(
#         in_addr=args['geckocore']['in_addr'],
#         out_addr=args['geckocore']['out_addr']
#     )
#     core.start()
#
#     p = GeckoSimpleProcess()
#     p.start(func=publish, name='publisher', kwargs=args)
#
#     s = GeckoSimpleProcess()
#     s.start(func=subscribe, name='subscriber', kwargs=args)
#
#
#     print("\n\n<<< press ctrl-c to exit >>>\n\n")
#     while True:
#         try:
#             time.sleep(1)
#         except KeyboardInterrupt:
#             print('main process got ctrl-c')
#             break
