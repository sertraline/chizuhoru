#!/usr/bin/python3
import mss
import aggdraw
from subprocess import call
from copy import copy
from os import path, remove
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw
import json
import re
import requests

SHOTNAME = "{}.png".format(datetime.now().strftime("%d_%b_%Y_%H:%M:%S"))
SHOTPATH = ["/tmp/{}".format(SHOTNAME), None]

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        if len(self.items) < 10:
            self.items.append(item)
        else:
            self.pop()
            self.items.append(item)
            
    def pop(self):
        self.items.reverse()
        self.items.pop()
        self.items.reverse()

    def extract(self):
        if not self.isEmpty():
            item = self.items[(len(self.items) - 1)]
            item.save(SHOTPATH[0])
            self.items.pop()

class NoLinkException(Exception):
    pass

def scrot(path):
    sct = mss.mss()
    try:
        filename = sct.shot(mon=-1, output=path)
    except PermissionError as e:
        print("Error writting to '{}':".format(path), e)
        sys.exit(1)

def convert(rectwidth, rectheight, rectx, recty, SHOTPATH, clip=1, shadow=0, shadowargs=[]):
    """Crops an image with given coordinates of selected rectangle; if
    no rectangle given, saves the image to the clipboard."""
    img = Image.open(SHOTPATH[0])
    if not "-" in str(rectwidth) and "-" not in str(rectheight):
        crop = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
    else:
        if "-" in str(rectwidth):
            rectx = rectx + rectwidth
            rectwidth = abs(rectwidth)
        if "-" in str(rectheight):
            recty = recty + rectheight
            rectheight = abs(rectheight)
        crop = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
    if shadow == 1:
        crop = drawshadow(crop, shadowargs[0], shadowargs[1], shadowargs[2])
    if SHOTPATH[1] != None:
        crop.save(SHOTPATH[1])
        if clip == 1:
            call(["xclip", "-sel", "clip", "-t", "image/png", SHOTPATH[1]])
    else:
        crop.save(SHOTPATH[0])
        if clip == 1:
            call(["xclip", "-sel", "clip", "-t", "image/png", SHOTPATH[0]])

def blur(rectwidth, rectheight, rectx, recty, SHOTPATH, actions):
    """Blurs a rectangle with given coordinates"""
    img = Image.open(SHOTPATH[0])
    actions.push(copy(img))
    if not "-" in str(rectwidth) and "-" not in str(rectheight):
        filt = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
        filt = filt.filter(ImageFilter.BLUR)
        img.paste(filt, (rectx, recty, (rectwidth + rectx), (rectheight + recty)))
        img.save(SHOTPATH[0])
    else:
        if "-" in str(rectwidth):
            rectx = rectx + rectwidth
            rectwidth = abs(rectwidth)
        if "-" in str(rectheight):
            recty = recty + rectheight
            rectheight = abs(rectheight)
        filt = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
        filt = filt.filter(ImageFilter.BLUR)
        img.paste(filt, (rectx, recty, (rectwidth + rectx), (rectheight + recty)))
        img.save(SHOTPATH[0])

def circle(begin, end, thickness, actions, pen, brush):
    """Draws a circle using aggdraw module"""
    img = Image.open(SHOTPATH[0])
    actions.push(copy(img))
    used = aggdraw.Draw(img)
    apen = aggdraw.Pen(pen, width=thickness)
    x0, y0 = (begin.x(), begin.y())
    x1, y1 = (end.x(), end.y())
    if x0 > x1 and y0 > y1:
        x0, y0, x1, y1 = (x1, y1, x0, y0)
    elif x0 > x1 and y0 < y1:
        x0, x1 = (x1, x0)
    elif x0 < x1 and y0 > y1:
        y0, y1 = (y1, y0)
    if brush == 1:
        brush = aggdraw.Brush(pen)
        used.ellipse((x0, y0, x1, y1), apen, brush)
    else:
        used.ellipse((x0, y0, x1, y1), apen)
    used.flush()
    img.save(SHOTPATH[0])

def drawrectangle(begin, end, thickness, actions, pen, brush):
    """Draws a rectangle using aggdraw module"""
    img = Image.open(SHOTPATH[0])
    actions.push(copy(img))
    used = aggdraw.Draw(img)
    apen = aggdraw.Pen(pen, width=thickness)
    x0, y0, x1, y1 = (begin.x(), begin.y(), end.x(), end.y())
    if x0 > x1 and y0 > y1:
        x0, y0, x1, y1 = (x1, y1, x0, y0)
    elif x0 > x1 and y0 < y1:
        x0, x1 = (x1, x0)
    elif x0 < x1 and y0 > y1:
        y0, y1 = (y1, y0)
    if brush == 1:
        brush = aggdraw.Brush(pen)
        used.rectangle((x0, y0, x1, y1), apen, brush)
    else:
        used.rectangle((x0, y0, x1, y1), apen)
    used.flush()
    img.save(SHOTPATH[0])

def drawline(begin, end, thickness, actions, pen):
    """Draws a line using aggdraw module"""
    img = Image.open(SHOTPATH[0])
    actions.push(copy(img))
    used = aggdraw.Draw(img)
    apen = aggdraw.Pen(pen, width=thickness)
    x0, y0, x1, y1 = (begin.x(), begin.y(), end.x(), end.y())
    used.line((x0, y0, x1, y1), apen)
    used.flush()
    img.save(SHOTPATH[0])

def drawshadow(image, space=84, shadow_space=20, iterations=46):
    #https://code.activestate.com/recipes/474116-drop-shadows-with-pil/ this helped me much
    free_space = space - shadow_space
    side_space = free_space//2
    background = (255, 255, 255, 0)
    shadow = "#707070"
    completeWidth = image.size[0] + space
    completeHeight = image.size[1] + space
    back = Image.new("RGBA", (completeWidth, completeHeight), background)
    back.paste(shadow, [side_space, side_space, (completeWidth - side_space), (completeHeight - side_space)])
    for i in range(0, iterations):
        back = back.filter(ImageFilter.BLUR)
    back.paste(image, ((side_space+shadow_space//2), side_space))
    return back

def custom_upload(shotpath, SHOTNAME, customArgs):
    access_token, username, password, bool_name, link = customArgs
    headers = None
    auth = None
    response = ""
    name = SHOTNAME
    if link == "None" or not link:
        raise NoLinkException
    if access_token != "None":
        headers = {'Authorization': access_token}
    if username != "None" and password != "None":
        auth = (username, password)
    if bool_name == True:
        if not ".png" in name:
            for c, i in enumerate((".jpg", ".jpeg")):
                if name.endswith(i):
                    name = name.replace(i, ".png")
                    break
                elif c == 1:
                    name = name + ".png"
                    print(name)
                    break
        files = {
            'name': (None, name),
            'file': (shotpath, open(shotpath, 'rb')),
        }
    else:
        files = {
            'file': (shotpath, open(shotpath, 'rb'))
        }
    if headers != None:
        response = requests.post(link, headers=headers, files=files)
    elif auth != None:
        response = requests.post(link, auth=auth, files=files)
    else:
        response = requests.post(link, files=files)
    result = response.text
    if "<a href=" in result:
        urls = re.search(r'(https?://|http?://)(?:[-\w.]|(?:%[\da-fA-F]{2}))+', link)
        reeeeeeee = r'href=[\'"]?([^\'" >]+)'
        url = re.findall(reeeeeeee, result)
        for i in url:
            if urls.group(0) in i:
                return i
    else:
        return response.text

def imgur_upload(shotpath, customArgs):
    imgur_id, imgur_link = customArgs
    if not imgur_link:
        raise NoLinkException
    headers = {
        'Authorization': 'Client-ID {}'.format(imgur_id),
    }
    files = {
        'image': (shotpath, open(shotpath, 'rb')),
    }
    response = requests.post(imgur_link, headers=headers, files=files)
    jtext = json.loads(response.text)
    return jtext["data"]["link"]
