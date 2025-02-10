# import os
# import sys


# sys.path.insert(0, os.path.dirname(__file__))


# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     message = 'It works!\n'
#     version = 'Python %s\n' % sys.version.split()[0]
#     response = '\n'.join([message, version])
#     return [response.encode()]

import os
import sys

# Menambahkan path direktori saat ini ke sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Mengimpor aplikasi Flask dari run.py
from run import app as application

