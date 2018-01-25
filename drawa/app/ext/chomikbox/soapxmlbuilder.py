from xml.etree import ElementTree as etree


class SOAPXMLBuilder(object):
    _root = etree.ElementTree()
    _xml_declaration = """<?xml version="1.0" encoding="UTF-8"?>"""

    _attributes_chars = [
        '-',  # ELEMENT ATTRIBUTE
        "#"  # ELEMENT TEXT
    ]

    def convert(self, xml_dict):
        for index, (key, value) in enumerate(xml_dict.items()):
            if index == 0:
                new_elem = self.__set_attributes(value, etree.Element(key))
                new_elem = self.__set_childs(value, new_elem)
                self._root = new_elem

        tree = etree.ElementTree(self._root)
        s = tree.getroot()

        return (self._xml_declaration + etree.tostring(s, encoding='unicode', method='xml'))

    def __set_childs(self, xml_dict, base_elem):
        for i, (key, value) in enumerate(xml_dict.items()):
            elem_type = type(value).__name__
            if key[:1] not in self._attributes_chars:  # CHECK IS ELEMENT, NOT ATTRIBUTE OR TEXT
                if elem_type == 'dict':
                    new_elem = self.__set_attributes(value, etree.Element(key))
                    new_elem = self.__set_childs(value, new_elem)
                    base_elem.append(new_elem)
                if elem_type == 'str':
                    new_elem = etree.Element(key)
                    new_elem.text = value
                    base_elem.append(new_elem)

        return base_elem

    def __set_attributes(self, xml_dict, base_elem):
        for i, (key, value) in enumerate(xml_dict.items()):
            if key[:1] == "-":  # ELEMENT ATTRIBUTE
                base_elem.set(key[1:], value)
            if key == "#text":  # ELEMENT TEXT
                base_elem.text = value

        return base_elem


if __name__ == "__main__":
    print("Examples: ")
    x = SOAPXMLBuilder()

    # 'SOAPAction': 'http://chomikuj.pl/IChomikBoxService/Auth
    json_auth = {
        "s:Envelope": {
            "-xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "-s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/",
            "s:Body": {
                "Auth": {
                    "-xmlns": "http://chomikuj.pl/",
                    "name": "qweqweqwe",
                    "passHash": "qqqqq",
                    "ver": "4"
                }
            }
        }
    }
    # http://chomikuj.pl/IChomikBoxService/Download
    json_download_disposition = {
        "s:Envelope": {
            "-xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "-s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/",
            "s:Body": {
                "Download": {
                    "-xmlns": "http://chomikuj.pl/",
                    "token": "123",
                    "sequence": {
                        "stamp": "123456789",
                        "part": "0",
                        "count": "1"
                    },
                    "disposition": "download",
                    "list": {
                        "DownloadReqEntry": {"id": "/bubx2k/tcbr-2.2.24-2.3.5,3218343566.zip(archive)"}
                    }
                }
            }
        }
    }

    json_download_get_url = {
        "s:Envelope": {
            "-xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "-s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/",
            "s:Body": {
                "Download": {
                    "-xmlns": "http://chomikuj.pl/",
                    "token": "fe302553-64ad-445c-898e-9cc92c7c1358",
                    "sequence": {
                        "stamp": "123456789",
                        "part": "0",
                        "count": "1"
                    },
                    "disposition": "download",
                    "list": {
                        "DownloadReqEntry": {
                            "id": "3218343566",
                            "agreementInfo": {
                                "AgreementInfo": {
                                    "name": "own",
                                    "cost": "0"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    x.convert(json_auth)
    x.convert(json_download_disposition)
    print(x.convert(json_download_get_url))
