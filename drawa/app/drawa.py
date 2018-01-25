import logging
import os
import string
import time
from functools import wraps

from flask import Flask, render_template, jsonify, request, Response

from .config import config_parser
from .aria2client import Aria2Client
from .pluginmanager import *

logging.basicConfig(level=logging.INFO, format='%(threadName)s:\t %(message)s')
logger = logging.getLogger(__name__)


class Drawa(Flask):
    def __init__(self, name):
        Flask.__init__(self, name)
        self.template_folder = os.path.join(os.path.dirname(__file__), 'www', 'templates')
        logger.info("Templates directory: {0}".format(self.template_folder))
        self.static_folder = os.path.join(os.path.dirname(__file__), 'www', 'static')
        logger.info("Static files directory: {0}".format(self.static_folder))

        self.jinja_options = Flask.jinja_options.copy()
        self.jinja_options.update(dict(
            block_start_string='<%',
            block_end_string='%>',
            variable_start_string='%%',
            variable_end_string='%%',
            comment_start_string='<#',
            comment_end_string='#>',
        ))

        load_builtin_plugins(os.path.join(os.path.dirname(__file__), 'ext'))
        for ext in registry.get_plugins():
            logger.info('Extension {0} supports: {1}'.format(registry.get_name(ext),
                                                             " ".join(x for x in ext.get_uri_prefix())
                                                             ))

        self.__aria_host = config_parser.get('aria2', 'hostname')
        self.__aria_port = config_parser.get('aria2', 'port')
        self.__aria_config = os.path.expandvars(config_parser.get('aria2', 'config'))
        self.__aria_secret = config_parser.get('aria2', 'secret')
        self.aria_connector = Aria2Client(
            host=self.__aria_host,
            port=self.__aria_port,
            secret=self.__aria_secret,
            config_file=self.__aria_config
        )

    def connect_or_start_aria(self):
        if not self.aria_connector.check_aria_is_installed():
            logger.error('Aria2 is not installed. Exiting...')
            raise SystemExit

        aria_version = None
        try:
            aria_version = self.aria_connector.aria_get_version()
        except ConnectionRefusedError:
            logger.info('Aria2 is not running, starting...')
            self.aria_connector.start_aria()

        connection_try = 0
        while aria_version is None:
            logger.info("Waiting for Aria2")
            try:
                aria_version = self.aria_connector.aria_get_version()
            except ConnectionRefusedError:
                connection_try += 1
            finally:
                if aria_version is not None:
                    break
                if connection_try > 30:
                    logger.error("Cannot start Aria2")
                    raise SystemExit
                else:
                    time.sleep(1)

        logger.info('Aria2 Version: {0}'.format(aria_version['version']))

    def get_available_uri_prefixes(self):
        prefixes = []
        for ext in registry.get_plugins():
            for prefix in ext.get_uri_prefix():
                prefixes.append(prefix)

        return prefixes

    def __format_directory(self, dir):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        valid_dir = ''.join(c for c in dir if c in valid_chars)
        valid_dir = valid_dir.replace(' ', '_')
        return valid_dir

    def parse_opts(self, opts):
        global_opts = self.aria_connector.get_global_option()
        # Combine DIR if provided
        if 'dir' in global_opts and 'dir' in opts:
            opts['dir'] = os.path.join(global_opts['dir'],
                                       self.__format_directory(opts['dir']))

        return opts

    def get_uri(self, url):
        urls = registry.hook.get_urls(uri=url)
        merg = self.__walk_list(urls)
        return merg

    def __walk_list(self, uris):

        merged = []

        for item in uris:
            if type(item) is list:
                merged = merged + self.__walk_list(item)
            if type(item) is dict:
                merged.append(item)

        return merged

    def start_server(self):
        self.run()


app = Drawa(__name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    config_user = str(config_parser.get("drawa", "username"))
    config_password = str(config_parser.get("drawa", "password"))
    if len(config_user) == 0 and len(config_password) == 0:
        return None

    return str(username) == config_user and \
           str(password) == config_password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_auth(None, None) is None:
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route("/")
@requires_auth
def hello():
    return render_template('index.html')


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/<path:template>.html')
@requires_auth
def send_template(template):
    return render_template('{}.html'.format(template))


@app.route('/api/get_available_uris', methods=['GET'])
@requires_auth
def get_uri_prefixes():
    return jsonify(app.get_available_uri_prefixes())


@app.route("/api/getAriaVersion", methods=['GET'])
@requires_auth
def get_aria_version():
    return jsonify(app.aria_connector.aria_get_version())


@app.route("/api/addUri", methods=['POST'])
@requires_auth
def add_uri():
    uris = request.json['uris']
    uris = uris.split(";")

    added = []
    for uri in uris:
        for dl in app.get_uri(uri):
            dl_url = dl['url']
            dl_opts = {}
            if 'opts' in dl:
                dl_opts = dl['opts']
            app.parse_opts(dl_opts)
            logging.info('Adding new download: {0} with opts: {1}'.format(dl_url, dl_opts))
            added.append(app.aria_connector.add_uri(dl_url, dl_opts))

    return jsonify(added)


@app.route("/api/getStatus/<gid>", methods=['GET'])
@requires_auth
def get_status(gid):
    return jsonify(app.aria_connector.tell_status(gid))


@app.route("/api/getStats", methods=['GET'])
@requires_auth
def get_stats():
    return jsonify(app.aria_connector.get_stats())


@app.route("/api/getQueue", methods=['GET'])
@requires_auth
def get_queue():
    active = app.aria_connector.tell_active()
    waiting = app.aria_connector.tell_waiting()
    stopped = app.aria_connector.tell_stopped()

    data = active + waiting + stopped

    return jsonify(data)


@app.route("/api/getActive", methods=['GET'])
@requires_auth
def get_active():
    logger.info('getActive')
    return jsonify(app.aria_connector.tell_active())


@app.route("/api/getWaiting", methods=['GET'])
@requires_auth
def get_waiting():
    return jsonify(app.aria_connector.tell_waiting())


@app.route("/api/getStopped", methods=['GET'])
@requires_auth
def get_stopped():
    return jsonify(app.aria_connector.tell_stopped())


@app.route("/api/purgeResults/<gid>", methods=['DELETE'])
@app.route("/api/purgeResults", methods=['DELETE'])
@requires_auth
def purge_results(gid=None):
    if gid is None:
        return jsonify(app.aria_connector.purge_download_result())
    else:
        return jsonify(app.aria_connector.remove_download_result(gid))


@app.route("/api/pause/<gid>", methods=['PUT'])
@app.route("/api/pauseAll", methods=['PUT'])
@requires_auth
def pause(gid=None):
    if gid is None:
        return jsonify(app.aria_connector.pause_all())
    else:
        return jsonify(app.aria_connector.pause(gid))


@app.route("/api/unpause/<gid>", methods=['PUT'])
@app.route("/api/unpauseAll", methods=['PUT'])
@requires_auth
def unpause(gid=None):
    if gid is None:
        return jsonify(app.aria_connector.unpause_all())
    else:
        return jsonify(app.aria_connector.unpause(gid))


@app.route("/api/remove/<gid>", methods=['DELETE'])
@requires_auth
def remove(gid):
    return jsonify(app.aria_connector.remove(gid))
