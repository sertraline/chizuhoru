#!/usr/bin/python3
from datetime import datetime
import mss, mss.tools
import json
import uuid
import re
import os

import requests

from Xlib.display import Display

class NoLinkException(Exception):
    pass

class ImageToolkit():

    def __init__(self, app, config):
        self.app = app
        self.config = config

        self.timeout = 10

    def grep_window(self):
        """
        Get window coordinates under the mouse pointer.
        """
        display = Display()
        window = display.screen().root
        result = window.query_pointer()
        dims = result.child.get_geometry()
        return (dims.width, dims.height, dims.x, dims.y)


    def catbox_upload(self, config, filepath, randname=False, parent=False):
        link = "https://catbox.moe/user/api.php"

        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))
            return
        name = os.path.split(filepath)[1]
        if randname:
            name = str(uuid.uuid4())

        files = {
            'fileToUpload': (name, iof, 'image/png')
        }
        data = {
            'reqtype': 'fileupload',
            'userhash': ''
        }
        if parent:
            parent.out.clear()
            text = f'POST {link}\n\n'
            parent.out.setText(text)
        try:
            response = requests.post(link, data=data, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))
            return
        if parent:
            text = parent.out.toPlainText()
            text += f'{response}\n{response.headers}\n\n'
            text += f'{response.text}'
            parent.out.setText(text)
        return response.text


    def uguu_upload(self, config, filepath, randname=False, parent=False):
        link = "https://uguu.se/api.php?d=upload-tool"

        name = os.path.split(filepath)[1]
        if randname:
            name = str(uuid.uuid4())

        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))
            return

        files = {
            'name': (None, name),
            'file': (name, iof)
        }
        if parent:
            parent.out.clear()
            text = f'POST {link}\n\n'
            parent.out.setText(text)
        try:
            response = requests.post(link, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))
            return
        if parent:
            text = parent.out.toPlainText()
            text += f'{response}\n{response.headers}\n\n'
            text += f'{response.text}'
            parent.out.setText(text)
        return response.text


    def imgur_upload(self, config, filepath, randname=False, parent=False):
        imgur_id = config.parse['config']['imgur']['client_id']
        imgur_url = config.parse['config']['imgur']['link']
        headers = {
            'Authorization': 'Client-ID {}'.format(imgur_id),
        }

        name = os.path.split(filepath)[1]
        if randname:
            name = str(uuid.uuid4())

        try:
            iof = open(filepath, 'rb')
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))

        files = {
            'image': (name, iof),
        }
        if parent:
            parent.out.clear()
            text = f'POST {imgur_url}\n{headers}\n\n'
            parent.out.setText(text)
        try:
            response = requests.post(imgur_url, headers=headers, files=files, timeout=self.timeout)
        except Exception as e:
            if parent:
                parent.out.clear()
                parent.out.setText(str(e))
            return
        if parent:
            text = parent.out.toPlainText()
            text += f'{response}\n{response.headers}\n\n'
            text += f'{response.text}'
            parent.out.setText(text)
        jtext = json.loads(response.text)
        return jtext["data"]["link"]
