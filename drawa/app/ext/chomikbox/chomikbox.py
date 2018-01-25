from app.config import config_parser
from app.pluginmanager import hookimpl
from .chomikboxclient import ChomikBoxClient

URI_PREFIX = ['chomikbox:']


class ChomikboxUrlProvider(object):
    def __init__(self):
        self.username = config_parser.get('chomikbox', 'username')
        self.password = config_parser.get('chomikbox', 'password')
        self.chomikbox = ChomikBoxClient(username=self.username,
                                         password=self.password)

    def get_uri_prefix(self):
        return URI_PREFIX

    @hookimpl
    def get_urls(self, uri):
        self.chomikbox.auth()
        items = []
        for prefix in URI_PREFIX:
            if uri.startswith(prefix):
                url = uri[len(prefix):]
                queue = self.chomikbox.get_download_queue(url)
                print ("Queue: ", queue)
                for item in queue:
                    dl_item = {
                        "url": item['url'],
                        "opts": {
                            "dir": self.chomikbox.get_download_folder_name(),
                            "out": item['name'],
                        }
                    }
                    items.append(dl_item)
        return items
