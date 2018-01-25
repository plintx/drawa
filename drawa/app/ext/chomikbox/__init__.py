import logging

from app.config import config_parser
from app.pluginmanager import registry

__version__ = '0.1.0'

logger = logging.getLogger(__name__)


class Extension(object):
    dist_name = 'ChomikBox'
    ext_name = 'ChomikBoxUrlProvider'
    version = __version__

    def __init__(self, registry, config):
        self.registry = registry
        self.config = config

    @staticmethod
    def setup():
        if (config_parser.get('chomikbox', 'enabled') == 'True'):
            from .chomikbox import ChomikboxUrlProvider
            registry.register(ChomikboxUrlProvider(), "ChomikBoxUrlProvider")
        else:
            logger.info("Extension ChomikBox is disabled")
