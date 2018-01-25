import configparser
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(threadName)s:\t %(message)s')
logger = logging.getLogger(__name__)

config_parser = configparser.ConfigParser()


def read_config(path):
    if not os.path.exists(path):
        logger.info(
            'Loading config from %s failed; it does not exist', path)
        return
    if not os.access(path, os.R_OK):
        logger.info(
            'Loading config from %s failed; read permission missing',
            path)
        return

    logger.info('Reading config file: {0}'.format(path))
    try:
        config_parser.read([path])
    except Exception as e:
        logger.error('Cannot read config file. {0}'.format(e))


class FlaskConfig(object):
    DEBUG = False
    TESTING = False
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'www', 'templates')
    STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'www', 'static')


class DevelopmentConfig(FlaskConfig):
    """
    Development configurations
    """
    DEBUG = True
    ASSETS_DEBUG = True


class ProductionConfig(FlaskConfig):
    """
    Production configurations
    """
    DEBUG = False
