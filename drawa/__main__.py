#!/usr/bin/env python3

import argparse
import logging
import os

from app import config

logging.basicConfig(level=logging.INFO, format='%(threadName)s:\t %(message)s')
logger = logging.getLogger(__name__)

ENV = 'PROD'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="list of config files")
    args = parser.parse_args()

    if args.config is not None:
        config.read_config(os.path.join(os.path.dirname(__file__), 'default.conf'))
        for path in args.config.split(":"):
            config.read_config(path)
    else:
        config.read_config(os.path.join(os.path.dirname(__file__), 'default.conf'))
        config.read_config(os.path.expanduser('~/.config/drawa/drawa.conf'))

    run_server()


def run_server():
    from app.drawa import app as flask_app

    if ENV == 'PROD':
        flask_app.config.from_object(config.ProductionConfig)
        flask_app.logger.disabled = True
        werkzeug_log = logging.getLogger('werkzeug')
        werkzeug_log.setLevel(logging.ERROR)
    elif ENV == 'DEV':
        flask_app.config.from_object(config.DevelopmentConfig)

    flask_app.template_folder = config.FlaskConfig.TEMPLATE_FOLDER
    flask_app.static_folder = config.FlaskConfig.STATIC_FOLDER

    flask_app.connect_or_start_aria()

    host = config.config_parser.get('drawa', 'hostname')
    port = int(config.config_parser.get('drawa', 'port'))

    logging.info('Starting server at: {0}:{1}'.format(host, port))
    flask_app.run(
        host=host,
        port=port,
    )


if __name__ == '__main__':
    main()
