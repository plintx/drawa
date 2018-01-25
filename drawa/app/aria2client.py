import xmlrpc.client
import shutil
import logging
import subprocess
import threading
import time
import os

ARIA_HOST = 'localhost'
ARIA_PORT = 6680

logger = logging.getLogger(__name__)


class PopenThread(threading.Thread):
    def __init__(self, command):
        threading.Thread.__init__(self)
        self.stdout = None
        self.stderr = None
        self.command = command
        self.daemon = True
        self.process = None

    def start_command(self):
        self.process = subprocess.Popen(self.command,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def communicate(self):
        try:
            self.stdout, self.stderr = self.process.communicate()
        except ValueError:
            time.sleep(1)

    def run(self):
        self.start_command()
        while True:
            self.communicate()


class Aria2Client(object):
    def __init__(self, host=ARIA_HOST, port=ARIA_PORT, config_file=None, secret=None):
        self.aria_host = host
        self.aria_port = port
        self.aria_config_file = config_file
        self.aria_secret = secret
        self.use_secret = True
        self.aria_thread = None

        if not self.aria_secret:
            self.use_secret = False
        if not self.check_aria_is_installed():
            raise SystemError('Aria2 not installed')

        if not os.path.isfile(self.aria_config_file):
            raise SystemError('Cannot read Aria2 config file: {0}'.format(self.aria_config_file))
        logging.info('Reading Aria2 config file: {0}'.format(self.aria_config_file))

        server_uri = 'http://{0}:{1}/rpc'.format(self.aria_host, self.aria_port)
        logger.info('Aria2 RPC Server running at: {0}'.format(server_uri))
        self.rpc_client = xmlrpc.client.ServerProxy(server_uri)

    def start_aria(self):
        command = ['aria2c',
                   '--conf-path={0}'.format(self.aria_config_file),
                   '--enable-rpc',
                   '--rpc-listen-all=true',
                   '--rpc-listen-port={0}'.format(self.aria_port),
                   '--continue',
                   ]

        if self.use_secret:
            command.append('--rpc-secret={0}'.format(self.aria_secret))

        cmd_joined = ' '.join(command)
        logger.info("Starting Aria2: {0}".format(cmd_joined))
        self.aria_thread = PopenThread(cmd_joined)
        self.aria_thread.start()

    def get_aria_stderr(self):
        return self.aria_thread.stderr

    @staticmethod
    def check_aria_is_installed():
        return bool(shutil.which("aria2c"))

    def aria_get_version(self):
        resp = self.rpc_client.aria2.getVersion('token:{0}'.format(self.aria_secret))
        return resp

    def add_uri(self, uri, opts=None):
        return self.rpc_client.aria2.addUri('token:{0}'.format(self.aria_secret), [uri], opts)

    def tell_status(self, gid):
        return self.rpc_client.aria2.tellStatus('token:{0}'.format(self.aria_secret), str(gid))

    def tell_active(self):
        return self.rpc_client.aria2.tellActive('token:{0}'.format(self.aria_secret))

    def tell_waiting(self, offset=0, num=1000):
        return self.rpc_client.aria2.tellWaiting('token:{0}'.format(self.aria_secret), offset, num)

    def tell_stopped(self, offset=0, num=1000):
        return self.rpc_client.aria2.tellStopped('token:{0}'.format(self.aria_secret), offset, num)

    def purge_download_result(self):
        return self.rpc_client.aria2.purgeDownloadResult('token:{0}'.format(self.aria_secret))

    def remove_download_result(self, gid):
        return self.rpc_client.aria2.removeDownloadResult('token:{0}'.format(self.aria_secret), gid)

    def get_stats(self):
        stats = self.rpc_client.aria2.getGlobalStat('token:{0}'.format(self.aria_secret))
        return stats

    def get_global_option(self):
        return self.rpc_client.aria2.getGlobalOption('token:{0}'.format(self.aria_secret))

    def pause(self, gid):
        return self.rpc_client.aria2.pause('token:{0}'.format(self.aria_secret), gid)

    def pause_all(self):
        return self.rpc_client.aria2.pauseAll('token:{0}'.format(self.aria_secret))

    def unpause(self, gid):
        return self.rpc_client.aria2.unpause('token:{0}'.format(self.aria_secret), gid)

    def unpause_all(self):
        return self.rpc_client.aria2.unpauseAll('token:{0}'.format(self.aria_secret))

    def remove(self, gid):
        return self.rpc_client.aria2.remove('token:{0}'.format(self.aria_secret), gid)
