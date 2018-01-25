import platform
import sys
import os

if not (3,6) <= sys.version_info: # < (3,):
    sys.exit(
        'ERROR: PyAria2ng requires Python 3.6, but found %s.' %
        platform.python_version())

sys.path.append(os.path.dirname(__file__))