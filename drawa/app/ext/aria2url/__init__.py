import logging

from app.pluginmanager import registry

__version__ = '0.1.0'

logger = logging.getLogger(__name__)


class Extension(object):
    dist_name = 'Aria2Url'
    ext_name = 'Aria2UrlProvider'
    version = __version__

    def __init__(self):
        pass

    @staticmethod
    def setup():
        from .aria2url import Aria2UrlProvider
        registry.register(Aria2UrlProvider(), "Aria2UrlProvider")
