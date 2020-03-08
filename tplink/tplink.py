# -*- coding: utf-8 -*-
"""Main module."""
import base64
import re

import requests
from aiohttp.hdrs import (CONTENT_TYPE, COOKIE, REFERER)


class TpLinkClient(object):
    def __init__(self, password, host='192.168.1.1', username=None):
        self.host = host
        self.password = password

        self.parse_macs = re.compile(
            'MACAddress=([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:' +
            '[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})')

        self.parse_names = re.compile('hostName=(.*)')
        self.parse_active = re.compile('active=(.)')

    def get_connected_devices(self):
        b64_encoded_password = base64.b64encode(
            self.password.encode('ascii')).decode('ascii')
        cookie = 'Authorization=Basic {}' \
            .format(b64_encoded_password)

        payload = "[LAN_HOST_ENTRY#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        page = requests.post(
            'http://{}/cgi?5'.format(self.host),
            data=payload,
            headers={
                REFERER: "http://{}/".format(self.host),
                COOKIE: cookie,
                CONTENT_TYPE: "text/plain"
            },
            timeout=10)

        actives = self.parse_active.findall(page.text)
        mac_addresses = [mac for i, mac
                         in enumerate(self.parse_macs.findall(page.text))
                         if actives[i] == "1"]
        host_names = [host for i, host
                      in enumerate(self.parse_names.findall(page.text))
                      if actives[i] == "1"]

        return dict(zip(mac_addresses, host_names))
