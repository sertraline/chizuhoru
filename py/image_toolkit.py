#!/usr/bin/python3
from datetime import datetime
import mss, mss.tools
import json
import uuid
import re
import os

import requests

from Xlib.display import Display
from time import sleep

class NoLinkException(Exception):
    pass

class ImageToolkit():

    def __init__(self, app, config):
        self.app = app
        self.config = config

        self.timeout = 20

    def grep_window(self):
        """
        Get window coordinates under the mouse pointer.
        """
        display = Display()
        window = display.screen().root
        result = window.query_pointer()
        dims = result.child.get_geometry()
        return (dims.width, dims.height, dims.x, dims.y)

    def get_name(self, ext):
        name = str(uuid.uuid4())[:14].replace('-', '')
        if len(ext)>1:
            name = name+'.'+ext[-1]
        return name

    def catbox_upload(self, config, filepath, randname=False, parent=False):
        link = "https://catbox.moe/user/api.php"

        name = os.path.split(filepath)[1]
        ext = filepath.split('.')
        if randname:
            name = self.get_name(ext)
    
        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.emit([str(e), None])
            return str(e)

        files = {
            'fileToUpload': (name, iof, 'image/png')
        }
        data = {
            'reqtype': 'fileupload',
            'userhash': ''
        }
        if parent:
            text = f'POST {link}\n<{name}>\n\n'
            parent.emit([text, None])
        try:
            if parent:
                sleep(1)
            response = requests.post(link, data=data, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.emit([str(e)])
            return str(e)
        if parent:
            text = f'{response}\n{response.headers}\n\n{response.text}'
            parent.emit([text])
        return response.text


    def uguu_upload(self, config, filepath, randname=False, parent=False):
        link = "https://uguu.se/api.php?d=upload-tool"

        name = os.path.split(filepath)[1]
        ext = filepath.split('.')
        if randname:
            name = self.get_name(ext)

        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.emit([str(e), None])
            return str(e)

        files = {
            'name': (None, name),
            'file': (name, iof)
        }
        if parent:
            text = f'POST {link}\n<{name}>\n\n'
            parent.emit([text, None])
        try:
            if parent:
                sleep(1)
            response = requests.post(link, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.emit([str(e), None])
            return str(e)

        if parent:
            text = f'{response}\n{response.headers}\n\n{response.text}'
            parent.emit([text])
        return response.text


    def imgur_upload(self, config, filepath, randname=False, parent=False):
        imgur_id = config.parse['config']['imgur']['client_id']
        imgur_url = config.parse['config']['imgur']['link']
        headers = {
            'Authorization': 'Client-ID {}'.format(imgur_id),
        }

        name = os.path.split(filepath)[1]
        ext = filepath.split('.')
        if randname:
            name = self.get_name(ext)

        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.emit([str(e), None])
            return str(e), None

        files = {
            'image': (name, iof),
        }
        if parent:
            text = f'POST {imgur_url}\n{headers}\n<{name}>\n\n'
            parent.emit([text, None])
        try:
            if parent:
                sleep(1)
            response = requests.post(imgur_url, headers=headers, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.emit([str(e), None])
            return str(e), None
        if parent:
            text = f'{response}\n{response.headers}\n\n{response.text}'
            parent.emit([text])
        try:
            jtext = json.loads(response.text)
        except json.decoder.JSONDecodeError as e:
            if parent:
                parent.emit([str(e), None])
            return str(e), None
        return jtext["data"]["link"], jtext["data"]["deletehash"]
