#!/usr/bin/python3
import re
import json
import aggdraw
import requests
import binascii
import mss, mss.tools
from copy import copy
from io import BytesIO
from os import path, remove
from subprocess import call
from datetime import datetime
from Xlib.display import Display
from PIL import Image, ImageFilter, ImageDraw


SHOTNAME = "{}.png".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
SHOTPATH = ["/tmp/{}".format(SHOTNAME), None]
TEMP = ''


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        if len(self.items) < 25:
            self.items.append(item)
        else:
            self.pop()
            self.items.append(item)
            
    def pop(self):
        del self.items[0]

    def extract(self):
        global TEMP
        if not self.isEmpty():
            TEMP = self.items[(len(self.items) - 1)]
            self.items.pop()


class NoLinkException(Exception):
    pass


def scrot(screen=-1, path=""):
    """
    mss screenshot. 
    screen: screen count.
    path: path to save image. 
    path = processing.SHOTPATH[0] or processing.SHOTPATH[1] if -d is set.
    """
    global TEMP
    sct = mss.mss()
    mon = sct.monitors[screen+1]
    shot = sct.grab(mon)
    raw_bytes = mss.tools.to_png(shot.rgb, shot.size)
    if path:
        try:
            Image.open(BytesIO(raw_bytes)).save(path)
        except PermissionError as e:
            print(f"Error writting to '{path}': {e}")
            sys.exit(1)
    else:
        img = Image.open(BytesIO(raw_bytes))
        TEMP = img


def convert(rectangle_pos=[], clip=1, shadowargs=[]):
    """
    Crops an image with given coordinates of selected rectangle; if no rectangle is given, 
    saves the image to the clipboard.
    rectangle_pos = [rectangle width, rectangle height, rectangle x, rectangle y],
    where x, y: position relative to the original image.

    clip: call XClip if copy to clipboard is set.
    shadowargs: if not empty, gets shadow configuration from the user and passes it to drawshadow().
    """
    global TEMP, SHOTPATH
    img = TEMP
    rectwidth, rectheight, rectx, recty = rectangle_pos
    if "-" in str(rectwidth):
        rectx = rectx + rectwidth
        rectwidth = abs(rectwidth)
    if "-" in str(rectheight):
        recty = recty + rectheight
        rectheight = abs(rectheight)
    crop = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
    if shadowargs:
        crop = drawshadow(crop, shadowargs[0], shadowargs[1], shadowargs[2], shadowargs[3])
    if SHOTPATH[1] != None:
        crop.save(SHOTPATH[1])
        if clip == 1:
            call(["xclip", "-sel", "clip", "-t", "image/png", SHOTPATH[1]])
    else:
        crop.save(SHOTPATH[0])
        if clip == 1:
            call(["xclip", "-sel", "clip", "-t", "image/png", SHOTPATH[0]])


def grep_window():
    """
    Get window coordinates under the mouse pointer.
    """
    display = Display()
    window = display.screen().root
    result = window.query_pointer()
    dims = result.child.get_geometry()
    return (dims.width, dims.height, dims.x, dims.y)


def blur(rectangle_pos, actions):
    """
    Blurs a rectangle with given coordinates.
    rectangle_pos = [rectangle width, rectangle height, rectangle x, rectangle y],
    where x, y: position relative to the original image.

    actions: preserve copy on the Stack in order to use undo.
    """
    global TEMP
    img = TEMP
    rectwidth, rectheight, rectx, recty = rectangle_pos
    actions.push(copy(img))
    if "-" in str(rectwidth):
        rectx = rectx + rectwidth
        rectwidth = abs(rectwidth)
    if "-" in str(rectheight):
        recty = recty + rectheight
        rectheight = abs(rectheight)
    filt = img.crop((rectx, recty, (rectwidth + rectx), (rectheight + recty)))
    filt = filt.filter(ImageFilter.GaussianBlur(radius=4))
    img.paste(filt, (rectx, recty, (rectwidth + rectx), (rectheight + recty)))
    TEMP = img


def circle(begin, end, thickness, actions, pen, brush):
    """
    Draws a circle using aggdraw module.
    begin, end: QPoint coordinates.
    thickness: circle size.
    actions: preserve copy on the Stack in order to use undo.
    pen: circle color.
    """
    global TEMP
    img = TEMP
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
    TEMP = img


def drawrectangle(begin, end, thickness, actions, pen, brush):
    """
    Draws a rectangle using aggdraw module.
    begin, end: QPoint coordinates.
    thickness: rectangle size.
    actions: preserve copy on the Stack in order to use undo.
    pen: rectangle color.
    """
    global TEMP
    img = TEMP
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
    TEMP = img


def drawline(begin, end, thickness, actions, pen):
    """
    Draws a line using aggdraw module.
    begin, end: QPoint coordinates.
    thickness: line size.
    actions: preserve copy on the Stack in order to use undo.
    pen: line color.
    """
    global TEMP
    img = TEMP
    actions.push(copy(img))
    used = aggdraw.Draw(img)
    apen = aggdraw.Pen(pen, width=thickness)
    x0, y0, x1, y1 = (begin.x(), begin.y(), end.x(), end.y())
    used.line((x0, y0, x1, y1), apen)
    used.flush()
    TEMP = img


def drawshadow(image, space=150, shadow_space=4, iterations=26, round_corners=False):
    """
    Draws shadow around the image.
    image = PIL.Image.
    space: space around the image.
    shadow_space: shadow size.
    iterations: draw shadows n-times.
    round_corners: round original image corners.
    """
    free_space = space - shadow_space
    side_space = free_space//2
    background = (0, 0, 0, 0)
    shadow = "#3c3c3c"
    completeWidth = image.size[0] + space
    completeHeight = image.size[1] + space
    back = Image.new("RGBA", (completeWidth, completeHeight), background)
    back.paste(shadow, [side_space, (side_space+20), (completeWidth - side_space), (completeHeight - side_space)])
    for i in range(0, iterations):
        back = back.filter(ImageFilter.GaussianBlur(6))
    if round_corners:
        radius = 6
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha = Image.new('L', image.size, 255)
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, image.size[1] - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (image.size[0] - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (image.size[0] - radius, image.size[1] - radius))
        image.putalpha(alpha)
        back.paste(image, ((side_space+shadow_space//2), side_space), mask=image)
    else:
        back.paste(image, ((side_space+shadow_space//2), side_space))
    return back


def custom_upload(args=[], preset="custom"):
    """
    Uses retrieved arguments to upload screenshot.
    args = [access_token, username, password, send_filename, link_to_upload]
    preset: upload using already existing configuration. presets = ["uguu.se", "catbox.moe"]
    """
    global SHOTPATH, SHOTNAME
    shotpath = SHOTPATH[1] if SHOTPATH[1] else SHOTPATH[0]
    name = SHOTNAME
    name = name + ".png" if not ".png" in name.lower() else name
    if preset == "catbox.moe":
        link = "https://catbox.moe/user/api.php"
        im =  open(shotpath, 'rb')
        files = {
            'fileToUpload': (name, im, 'image/png')
        }
        data = {
            'reqtype': 'fileupload',
            'userhash': ''
        }
        response = requests.post(link, data=data, files=files)
    elif preset == "uguu.se":
        link = "https://uguu.se/api.php?d=upload-tool"
        files = {
            'name': (None, name),
            'file': (name, open(shotpath, 'rb'))
        }
        response = requests.post(link, files=files)
    else:
        access_token, username, password, bool_name, link = args
        headers = None
        auth = None
        if link == "None" or not link:
            raise NoLinkException
        if access_token != "None":
            headers = {'Authorization': access_token}
        if username != "None" and password != "None":
            auth = (username, password)
        if bool_name == True:
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
    if "<a href=" in response.text:
        try_find_name = re.search(rf'(?:http:\/\/|https:\/\/)([-\w.\/])+([-_\w\d.])*{name}', response.text)
        if try_find_name is not None:
            return try_find_name.group(0)
        try_find_png = re.search(r'(?:http:\/\/|https:\/\/)([-\w.\/])+([-_\w\d.])*\.png', response.text)
        if try_find_png is not None:
            return try_find_png.group(0)
        url = re.search(r'(?:https?:\/\/|http?:\/\/)(?:[-\w.]|(?:%[\da-fA-F]{2}))+', link)
        match = url.group(0).replace('https://', '').replace('http://', '')
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
        for item in urls:
            if match in item:
                return item
    else:
        return response.text


def imgur_upload(customArgs):
    """
    Uploads picture to imgur.
    customArgs = [imgur_user_id, imgur_user_link, copy_link_to_clipboard]
    """
    global SHOTPATH
    imgur_id, imgur_link, clipboard, called = customArgs
    if not imgur_link:
        raise NoLinkException
    shotpath = SHOTPATH[1] if SHOTPATH[1] else SHOTPATH[0]
    headers = {
        'Authorization': 'Client-ID {}'.format(imgur_id),
    }
    files = {
        'image': (shotpath, open(shotpath, 'rb')),
    }
    response = requests.post(imgur_link, headers=headers, files=files)
    jtext = json.loads(response.text)
    if clipboard or called:
        call(f"echo {jtext['data']['link']} | xclip -sel clip", shell=True)
    return jtext["data"]["link"]


def decode(image):
    """
    Decodes image with encoded LSB.
    image = PIL.Image. Is splitted into channels, red channel is used for decryption.
    Reads until delimiter after the user message.
    """
    red_channel, green_channel, blue_channel, *alpha = image.convert('RGB').split()
    x, y = image.size[0], image.size[1]  

    text = ''
    delim = '001011110010110100101111'

    for x_pixel in range(x):
        for y_pixel in range(y):
            bin_im_pixel = bin(red_channel.getpixel((x_pixel, y_pixel)))
            text += bin_im_pixel[-1]
            if len(text) > len(delim):
                if delim in text[-24:]:
                    text = text[:-24]
                    return (int(text, 2).to_bytes((len(text) + 7) // 8, 'big')).decode()
    
    return (int(text, 2).to_bytes((len(text) + 7) // 8, 'big')).decode()


def encode(text, image, savepath):
    """
    Encodes message to binary and changes image's least significant bit.
    text = message to encode. 
    image = PIL.Image. Is splitted into channels, red channel is used for encryption.
    Pushes delimiter after the user message.
    """
    red_channel, green_channel, blue_channel, *alpha = image.split()
    x, y = image.size[0], image.size[1]

    counter = 0
    delim = '001011110010110100101111'
    bin_text = bin(int(binascii.hexlify(text.encode()),16))[2:]

    for x_cord in range(x):
        for y_cord in range(y):
            if counter >= len(bin_text):
                if bin_text == delim:
                    if alpha:
                        result = Image.merge("RGBA", [red_channel, green_channel, blue_channel, alpha[0]])
                    else:
                        result = Image.merge("RGB", [red_channel, green_channel, blue_channel])
                    result.save(savepath, 'PNG')
                    return f"Saved!"
                counter = 0
                bin_text = delim
            bin_im_pixel = bin(red_channel.getpixel((x_cord, y_cord)))
            bin_im_pixel = bin_im_pixel[:-1] + '1' if bin_text[counter] == '1' else bin_im_pixel[:-1] + '0'

            red_channel.putpixel((x_cord, y_cord), int(bin_im_pixel, base=2))
            counter+=1