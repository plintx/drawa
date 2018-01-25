import hashlib
import logging
import re
import time
from xml.etree import ElementTree as et

from .soapclient import SOAPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChomikBoxClient(object):
    class AuthException(Exception):
        pass

    class DispositionException(Exception):
        pass

    SERVICE_URL = 'http://box.chomikuj.pl/services/ChomikBoxService.svc'

    def __init__(self, username=None, password=None):

        # Chomikuj session data
        self._hamsterId = 0
        self._token = ''
        self.account_balance = None
        self.file_ids = []

        # Object data

        self._username = None
        if username is not None:
            self.set_username(username)

        self._password = None
        if password is not None:
            self.set_password(password)

        self._soapclient = SOAPClient()
        self._soapclient.set_url(self.SERVICE_URL)
        self.__download_queue = []
        self.__download_folder = None

    def check_credentials(self):
        if self._username and self._password:
            return True

        return False

    def set_username(self, username):
        self._username = username

    def set_password(self, password):
        self._password = hashlib.md5(password.encode('utf-8')).hexdigest()

    def __parse_respone(self, response):

        response_xml = et.fromstring(response)
        # AUTH: if AuthResult with Status available
        auth_response = response_xml.find('.//{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}status')
        if auth_response is not None:
            status = auth_response.text
            if status.upper() == 'OK':
                self._token = response_xml.find('.//{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}token').text
                self._hamsterId = response_xml.find(
                    './/{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}hamsterId').text
                return True
            else:
                raise self.AuthException('Auth failed, bad username/password? Status: %s' % (status))
        # Check account balance available
        account_balance_response = response_xml.find(
            './/{http://chomikuj.pl/}DownloadResult/{http://chomikuj.pl}accountBalance/'
            '{http://chomikuj.pl/}transfer/{http://chomikuj.pl/}extra')
        if account_balance_response is not None:
            self.account_balance = account_balance_response.text
            # print ('Account balance: ', self.account_balance)

        # Download Folder?
        if self.__download_folder is None:
            download_folder = response_xml.find('.//{http://chomikuj.pl/}DownloadFolder')
            self.__download_folder = download_folder.find('{http://chomikuj.pl/}name').text

        # Download: if DownloadResult with Status available
        maybe_download = response_xml.find('.//{http://chomikuj.pl/}DownloadResult/{http://chomikuj.pl}status')
        if maybe_download is not None:
            status = maybe_download.text
            if status.upper() == 'OK':
                # Find all file entries
                for file_entry in response_xml.findall('.//{http://chomikuj.pl/}files/{http://chomikuj.pl/}FileEntry'):
                    # Get some info: file url and file id
                    file_url = file_entry.find('{http://chomikuj.pl/}url')
                    file_id = file_entry.find('{http://chomikuj.pl/}id')
                    file_name = file_entry.find('{http://chomikuj.pl/}name')
                    # If URL is None it's time to call to get that URL
                    if file_url.text is None:
                        # Get some info cost, and agreement
                        agreement = file_entry.find(
                            '{http://chomikuj.pl/}agreementInfo/{http://chomikuj.pl/}AgreementInfo/'
                            '{http://chomikuj.pl/}name')
                        cost = file_entry.find(
                            '{http://chomikuj.pl/}agreementInfo/{http://chomikuj.pl/}AgreementInfo/'
                            '{http://chomikuj.pl/}cost')
                        # Maybe downloading from your own box?
                        cost_int = 0
                        if cost.text is not None: cost_int = cost.text

                        # Check for available funds
                        if int(self.account_balance) >= int(cost_int):
                            # print ('Call for url')
                            self.__call_get_file_entry_url(file_id.text, agreement.text, cost_int)
                        else:
                            raise self.DispositionException(
                                'There is not enough funds for download file: %s' % (file_name.text))

                    else:  # URL is not None, so we can download the file
                        item = dict(id=file_id.text, url=file_url.text, name=file_name.text)
                        self.__download_queue.append(item)
            else:
                raise self.DispositionException(f'Wrong status for download disposition: {status}')

    def auth(self):
        soap_action = 'http://chomikuj.pl/IChomikBoxService/Auth'
        auth_dict = {
            's:Envelope': {
                '-xmlns:s': 'http://schemas.xmlsoap.org/soap/envelope/',
                '-s:encodingStyle': 'http://schemas.xmlsoap.org/soap/encoding/',
                's:Body': {
                    'Auth': {
                        '-xmlns': 'http://chomikuj.pl/',
                        'name': self._username,
                        'passHash': self._password,
                        'ver': '4'
                    }
                }
            }
        }
        xml = self._soapclient.json2xml(auth_dict)

        response = self._soapclient.call(soap_action, xml)
        return self.__parse_respone(response)

    def get_download_queue(self, url):
        self.__download_queue.clear()
        self.file_ids.clear()
        self.__call_download_disposition(url)
        return self.__download_queue

    def get_download_folder_name(self):
        return self.__download_folder

    def __call_download_disposition(self, url):
        file_url = re.search('[http|https]://chomikuj.pl(.*)', url).group(1)
        soap_action = 'http://chomikuj.pl/IChomikBoxService/Download'
        download_disposition_dict = {
            's:Envelope': {
                '-xmlns:s': 'http://schemas.xmlsoap.org/soap/envelope/',
                '-s:encodingStyle': 'http://schemas.xmlsoap.org/soap/encoding/',
                's:Body': {
                    'Download': {
                        '-xmlns': 'http://chomikuj.pl/',
                        'token': self._token,
                        'sequence': {
                            'stamp': int(time.time()),
                            'part': '0',
                            'count': '1'
                        },
                        'disposition': 'download',
                        'list': {
                            'DownloadReqEntry': {'id': file_url}
                        }
                    }
                }
            }
        }
        xml = self._soapclient.json2xml(download_disposition_dict)
        response = self._soapclient.call(soap_action, xml)
        self.__parse_respone(response)

    def __call_get_file_entry_url(self, file_id, file_agreement, file_cost):

        if file_id in self.file_ids:
            return
        else:
            self.file_ids.append(file_id)

        soap_action = 'http://chomikuj.pl/IChomikBoxService/Download'
        get_file_entry_url_dict = {
            's:Envelope': {
                '-xmlns:s': 'http://schemas.xmlsoap.org/soap/envelope/',
                '-s:encodingStyle': 'http://schemas.xmlsoap.org/soap/encoding/',
                's:Body': {
                    'Download': {
                        '-xmlns': 'http://chomikuj.pl/',
                        'token': self._token,
                        'sequence': {
                            'stamp': int(time.time()),
                            'part': '0',
                            'count': '1'
                        },
                        'disposition': 'download',
                        'list': {
                            'DownloadReqEntry': {
                                'id': file_id,
                                'agreementInfo': {
                                    'AgreementInfo': {
                                        'name': file_agreement,
                                        'cost': file_cost
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        xml = self._soapclient.json2xml(get_file_entry_url_dict)
        response = self._soapclient.call(soap_action, xml)
        self.__parse_respone(response)


