# ##############################################
# # The MIT License (MIT)
# # Copyright (c) 2014 Kevin Walchko
# # see LICENSE for full details
# ##############################################
# #
# from tempfile import NamedTemporaryFile
# from glob import glob
# import os
# import platform
# try:
#     import simplejson as json
# except ImportError:
#     import json
#
#
# class CoreFile(object):
#     fd = None
#     def __init__(self, in_addr, out_addr, dir='/tmp'):
#         prefix = 'gecko'
#
#         # windows sucks!
#         if platform.system() == 'Windows':
#             dir = ''
#
#         # check for old stale gecko json files and remove them
#         stale = glob(dir + '/' + prefix + '*.json')
#         for f in stale:
#             os.remove(f)
#
#         data = {'in_addr': in_addr, 'out_addr': out_addr}
#         self.fd = NamedTemporaryFile(dir=dir, prefix='gecko', suffix='.json', delete=True)
#         self.fd.write(json.dumps(data).encode('utf8'))
#         self.fd.flush()
#         self.name = self.fd.name
#
#     def __del__(self):
#         self.close()
#
#     def close(self):
#         if self.fd:
#             self.fd.close()
