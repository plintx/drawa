from urllib.parse import urlsplit

import requests

from . import soapxmlbuilder


class SOAPClient(object):
    def __init__(self):
        self._session = requests.Session()
        self._url = None
        self._host = None
        self._xmlbuilder = soapxmlbuilder.SOAPXMLBuilder()

    def set_url(self, url):
        self._url = url
        self._set_host(url)

    def _set_host(self, url):
        host = "{0.netloc}".format(urlsplit(url))
        self._host = host

    def json2xml(self, json_data):
        return self._xmlbuilder.convert(json_data)

    def call(self, soap_action: "SOAP Action String", xml_body: "SOAP XML Body", url: "URL (override)" = None,
             host: "HOST (override)" = None):

        if url is None:
            url = self._url

        if host is None:
            host = self._host

        headers = {
            "SOAPAction": soap_action,
            "Content-Encoding": "identity",
            "Content-Type": "text/xml;charset=utf-8",
            "Content-Length": str(len(xml_body)),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "identity",
            "Accept-Language": "pl-PL,en,*",
            "User-Agent": "Python-chomikbox client",
            "Host": host,
        }

        response = self._session.post(url, data=xml_body, headers=headers)

        if response.status_code is not 200:
            response.raise_for_status()
        return response.content


if __name__ == '__main__':
    pass
