from app.pluginmanager import hookimpl

URI_PREFIX = ['ftp://', 'http://', 'https://', 'magnet:']


class Aria2UrlProvider(object):
    def __init__(self):
        pass

    @staticmethod
    def get_uri_prefix():
        return URI_PREFIX

    @hookimpl
    def get_urls(self, uri):
        if str(uri).startswith(tuple(URI_PREFIX)):
            return {"url": uri}
