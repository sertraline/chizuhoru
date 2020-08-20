from screenshot import ScreenshotCLI
from PyQt5.QtGui import QPainter, QImage, QPalette, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, QPoint
from PyQt5 import QtCore

from datetime import datetime
import json
import os

import qt_toolkit
from main_window import HistoryItem

class EventHistory:
    def __init__(self):
        self.pen = []
        self.rect = []
        self.circle = []
        self.line = []
        self.free = []

        # string takes less memory than a list
        self.sequence = ''

class ScreenWindow(qt_toolkit.BaseLayerCanvas):

    def __init__(self, parent, app, config, image_toolkit):
        super().__init__()

        self.parent = parent
        self.app = app
        self.config = config
        self.screen_unit = ScreenshotCLI()

        save_dir = self.config.parse["config"]["default_dir"]
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        filename_format = self.config.parse["config"]["filename_format"]
        filename = "{}.png".format(datetime.now().strftime(filename_format))
        self.filepath = os.path.join(save_dir, filename)

        # move instance to current screen
        self.move(self.left, self.top)

        # make a screenshot
        self.temp = self.screen_unit.shot(self.screen)
        self.temp.seek(0)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.Tool)
        self.setMouseTracking(True)

        # define image processing methods separated from GUI
        self.img_toolkit = image_toolkit
        # define right-click control menu
        self.toolkit = qt_toolkit.Toolkit(self, self.config)

        self.showFullScreen()
        self.render_background()

        # RightMouseButton -> paint_allowed = False
        # LeftMouseButton  -> paint_allowed = True
        self.paint_allowed = True
        # last selection rectangle
        # LeftMouseButton -> self.sel_rect = None
        self.sel_rect = None

        # track history to undo actions
        self.history = EventHistory()

        # image history (save, upload)
        _dirpath = os.path.dirname(os.path.realpath(__file__))
        self.hist_dir = os.path.join(_dirpath, '../.history')
        self.hist = os.path.join(self.hist_dir, 'index.json')

        # coordinates of X11 window under mouse button
        self.cords = None

        self.quadratic = False

        self.pen_point_list = []
        self.pen_cords_track_list = []


    def render_background(self):
        qimg = QtGui.QPixmap()
        qimg.loadFromData(self.temp.getvalue())
        scale = qimg.scaled(QSize(self.width, self.height))
        self.setPixmap(scale)

    def paintEvent(self, event):
        super(ScreenWindow, self).paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setBrush(QtGui.QBrush(self.toolkit.brush_selection_color))
        painter.setPen(QtGui.QPen(self.toolkit.pen_selection_color, 2, Qt.DashLine))

        if not self.cords:
            rect = QtCore.QRect(self.begin, self.end)
            if self.quadratic:
                rect = self.rect_quadratic(rect)

            # if paint tool is selected and LMB clicked, process event
            if self.paint_allowed:
                # switch 1: pen drawing, switch 5: free drawing
                if self.toolkit.switch == 5:
                    if self.pen_cords_track_list:
                        for point in self.pen_cords_track_list:
                            painter.drawPoint(point[0], point[1])
                elif self.toolkit.switch == 2:
                    painter.drawEllipse(rect)
                elif self.toolkit.switch == 3:
                    painter.drawRect(rect)
                elif self.toolkit.switch == 4:
                    painter.drawLine(self.begin.x(), self.begin.y(),
                                     self.end.x(), self.end.y())
                else:
                    # switch 0: selection
                    if self.begin != self.end:
                        painter.drawRect(rect)
                        self.sel_rect = rect
            else:
                # redraw last selection rectangle on RMB click
                if self.sel_rect is not None and self.toolkit.switch == 0:
                    painter.drawRect(self.sel_rect)
        else:
            painter.drawRect(self.cords)
            self.sel_rect = self.cords
            self.cords = None

    def closeScreen(self):
        self.toolkit.close()
        self.deleteLater()
        self.close()
  
    def hideScreen(self):
        self.hide()
        self.toolkit.hide()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.paint_allowed = False
            if self.toolkit.isVisible():
                self.toolkit.close()
            else:
                self.toolkit.show()
            return
        if event.buttons() == QtCore.Qt.LeftButton:
            self.paint_allowed = True
            self.sel_rect = None

            if self.toolkit.switch == 5:
                self.pen_point_list = []
            self.begin = event.pos()
            self.end = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        painter = QPainter(self.pixmap())
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(self.toolkit.pen_color, self.toolkit.pen_size))

        # switch 1: pen drawing, switch 5: free drawing
        if (self.toolkit.switch == 1 or self.toolkit.switch == 5) \
            and event.buttons() == QtCore.Qt.LeftButton:
            if self.last_x is None:
                self.last_x = event.x()
                self.last_y = event.y()
                return

            if abs(self.last_x - event.x()) > 4 or \
                abs(self.last_y - event.y() > 4):
                # reset last mouse coordinates if 
                # distance between points is too big
                self.last_x = event.x()
                self.last_y = event.y()

            pen = QtGui.QPen(self.toolkit.pen_color, self.toolkit.pen_size,
                             self.toolkit.pen_style, self.toolkit.cap, self.toolkit.joint)
            brush = QtGui.QBrush(self.toolkit.brush_color)
            painter.setBrush(brush)
            painter.setPen(pen)

            if self.toolkit.switch == 5:
                draw_args = QtCore.QPoint(self.last_x, self.last_y)
                self.pen_point_list.append(draw_args)
                self.pen_cords_track_list.append((event.x(), event.y()))
            else:
                draw_args = ((self.last_x, self.last_y, event.x(), event.y()),
                              pen, brush)
                if len(self.history.pen) == 0:
                    self.history.sequence += 'p'
                    self.history.pen.append([])
                else:
                    if len(self.history.pen[-1]) < 10:
                        self.history.pen[-1].append(draw_args)
                    else:
                        self.history.sequence += 'p'
                        self.history.pen.append([])
                        self.history.pen[-1].append(draw_args)

                painter.drawLine(*draw_args[0])

            self.update()
            self.last_x = event.x()
            self.last_y = event.y()

        elif event.buttons() == QtCore.Qt.LeftButton:
            self.end = event.pos()
            self.update()

    def buildPath(self):
        factor = 0.4
        points = self.pen_point_list
        self.path = QtGui.QPainterPath(points[0])
        cp1 = None
        if len(points) > 5:
            # throw away excess points to make curve smooth
            points = points[::5]
        for p, current in enumerate(points[1:-1], 1):
            # previous segment
            source = QtCore.QLineF(points[p - 1], current)
            # next segment
            target = QtCore.QLineF(current, points[p + 1])
            targetAngle = target.angleTo(source)
            if targetAngle > 180:
                angle = (source.angle() + source.angleTo(target) / 2) % 360
            else:
                angle = (target.angle() + target.angleTo(source) / 2) % 360

            revTarget = QtCore.QLineF.fromPolar(source.length() * factor,
                                                angle + 180).translated(current)
            cp2 = revTarget.p2()

            try:
                if p == 1:
                    self.path.quadTo(cp2, current)
                else:
                    if cp1:
                        self.path.cubicTo(cp1, cp2, current)
            except TypeError:
                return None

            revSource = QtCore.QLineF.fromPolar(target.length() * factor,
                                                angle).translated(current)
            cp1 = revSource.p2()
        if cp1:
            self.path.quadTo(cp1, points[-1])

    def rect_quadratic(self, rect):
        rectx, recty, rectw, recth = list(rect.getRect())
        if not '-' in str(recth) and not '-' in str(rectw):
            if rectw > recth:
                rect = [rectx, recty, recth, recth]
            else:
                rect = [rectx, recty, rectw, rectw]
        else:
            if '-' in str(rectw) and not '-' in str(recth):
                ab_w = abs(rectw)
                if ab_w > recth:
                    rect = [rectx, recty, -recth, recth]
                else:
                    rect = [rectx, recty, rectw, ab_w]
            elif '-' in str(recth) and not '-' in str(rectw):
                ab_h = abs(recth)
                if ab_h > recth:
                    rect = [rectx, recty, rectw, -rectw]
                else:
                    rect = [rectx, recty, ab_h, -recth]
            else:
                if rectw > recth:
                    rect = [rectx, recty, recth, recth]
                else:
                    rect = [rectx, recty, rectw, rectw]
        return QtCore.QRect(*rect)

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

        if self.toolkit.switch == 0:
            return
        if self.begin == self.end:
            return
        if not self.paint_allowed:
            return

        painter = QPainter(self.pixmap())
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        pen = QtGui.QPen(self.toolkit.pen_color, self.toolkit.pen_size,
                         self.toolkit.pen_style, self.toolkit.cap, self.toolkit.joint)
        outline = self.config.parse['config']['canvas']['outline']
        if outline == 'disabled':
            pen_outline = None
        else:
            if outline == 'black':
                out_color = QtGui.QColor('black')
            else:
                out_color = self.toolkit.brush_color
                out_color = out_color.toRgb()
                out_color.setAlpha(255)
            pen_outline = QtGui.QPen(out_color, self.toolkit.pen_size+2,
                                     self.toolkit.pen_style, self.toolkit.cap,
                                     self.toolkit.joint)
        brush = QtGui.QBrush(self.toolkit.brush_color)
        painter.setBrush(brush)
        painter.setPen(pen)

        rect = QtCore.QRect(self.begin, self.end)
        if self.quadratic:
            rect = self.rect_quadratic(rect)

        if self.toolkit.switch == 5:
            self.buildPath()
            if not self.path:
                return
            self.history.sequence += 'f'
            self.history.free.append((self.path, pen, brush, pen_outline))

            if pen_outline:
                painter.setPen(pen_outline)
                painter.drawPath(self.path)
                painter.setPen(pen)
            painter.drawPath(self.path)

            self.pen_cords_track_list = []
            return
        # draw on pixmap
        if self.toolkit.switch == 2:
            self.history.sequence += 'c'
            self.history.circle.append((rect, pen, brush, pen_outline))
            if pen_outline:
                painter.setPen(pen_outline)
                painter.drawEllipse(rect)
                painter.setPen(pen)
            painter.drawEllipse(rect)
        elif self.toolkit.switch == 3:
            self.history.sequence += 'r'
            self.history.rect.append((rect, pen, brush, pen_outline))
            if pen_outline:
                painter.setPen(pen_outline)
                painter.drawRect(rect)
                painter.setPen(pen)
            painter.drawRect(rect)
        elif self.toolkit.switch == 4:
            self.history.sequence += 'l'
            self.history.line.append(((self.begin.x(), self.begin.y(),
                                       self.end.x(), self.end.y()),
                                       pen, brush, pen_outline))
            if pen_outline:
                painter.setPen(pen_outline)
                painter.drawLine(self.begin.x(), self.begin.y(),
                                 self.end.x(), self.end.y())
                painter.setPen(pen)
            painter.drawLine(self.begin.x(), self.begin.y(),
                             self.end.x(), self.end.y())
        
        self.update()

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def wheelEvent(self, event):
        if self.toolkit.isVisible():
            self.toolkit.color_selected()
            return
        if self.toolkit.tools_config.isVisible():
            self.toolkit.tools_config_outline.setWindowOpacity(0)
            self.toolkit.tools_config.close()
            self.toolkit.tools_config_outline.close()
        else:
            self.toolkit.tools_config_outline.setWindowOpacity(0)
            self.toolkit.tools_config_outline.setStyleSheet("background: #131313;")
            self.toolkit.tools_config_outline.show()
            self.toolkit.tools_config_outline.setWindowOpacity(0.6)
            self.toolkit.tools_config_outline.raise_()
            self.toolkit.tools_config.setWindowOpacity(1)
            self.toolkit.tools_config.show()
            self.toolkit.tools_config.raise_()

    def keyPressEvent(self, qKeyEvent):
        if (qKeyEvent.modifiers() & Qt.ShiftModifier):
            self.quadratic = True
            return
        # is responsible for Ctrl-Z both in English and Cyrillic moonspeak
        elif (qKeyEvent.nativeModifiers() == 4 or qKeyEvent.nativeModifiers() == 8196
           ) and (qKeyEvent.nativeScanCode() == 52) and len(self.history.sequence) != 0:

            self.render_background()

            painter = QPainter(self.pixmap())
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            pen = QtGui.QPen(self.toolkit.pen_color, self.toolkit.pen_size)
            painter.setPen(pen)

            pen_cnt = -1
            circl_cnt = -1
            rect_cnt = -1
            line_cnt = -1
            free_cnt = -1
            for item in self.history.sequence[:-1]:
                if item == 'p':
                    pen_cnt += 1
                    args = self.history.pen[pen_cnt]
                    for pack in args:
                        painter.setPen(pack[1])
                        painter.setBrush(pack[2])
                        painter.drawLine(*pack[0])
                elif item == 'c':
                    circl_cnt += 1
                    args = self.history.circle[circl_cnt]
                    if args[-1]:
                        painter.setPen(args[-1])
                        painter.setBrush(args[2])
                        painter.drawEllipse(args[0])
                    painter.setPen(args[1])
                    painter.setBrush(args[2])
                    painter.drawEllipse(args[0])
                elif item == 'r':
                    rect_cnt += 1
                    args = self.history.rect[rect_cnt]
                    if args[-1]:
                        painter.setPen(args[-1])
                        painter.setBrush(args[2])
                        painter.drawRect(args[0])
                    painter.setPen(args[1])
                    painter.setBrush(args[2])
                    painter.drawRect(args[0])
                elif item == 'l':
                    line_cnt += 1
                    args = self.history.line[line_cnt]
                    if args[-1]:
                        painter.setPen(args[-1])
                        painter.setBrush(args[2])
                        painter.drawLine(*args[0])
                    painter.setPen(args[1])
                    painter.setBrush(args[2])
                    painter.drawLine(*args[0])
                elif item == 'f':
                    free_cnt += 1
                    args = self.history.free[free_cnt]
                    if args[-1]:
                        painter.setPen(args[-1])
                        painter.setBrush(args[2])
                        painter.drawPath(args[0])
                    painter.setPen(args[1])
                    painter.setBrush(args[2])
                    painter.drawPath(args[0])
            last_item = self.history.sequence[-1]
            if last_item == 'p':
                self.history.pen.pop(-1)
            elif last_item == 'c':
                self.history.circle.pop(-1)
            elif last_item == 'r':
                self.history.rect.pop(-1)
            elif last_item == 'l':
                self.history.line.pop(-1)
            elif last_item == 'f':
                self.history.free.pop(-1)
            self.history.sequence = self.history.sequence[:-1]
            painter.end()

        elif qKeyEvent.key() == QtCore.Qt.Key_Return:
            self.save_image(clip_only=True)
            self.closeScreen()

        elif qKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.closeScreen()

        elif qKeyEvent.nativeScanCode() == 28: #"T" key
            if self.toolkit.isVisible():
                self.toolkit.hide()
            else:
                self.toolkit.show()

        elif qKeyEvent.nativeScanCode() == 39: #"S" key
            self.save_image()
            self.hideScreen()

        elif qKeyEvent.nativeScanCode() == 38: #"A" key
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                                | Qt.WindowTransparentForInput \
                                | QtCore.Qt.FramelessWindowHint \
                                | QtCore.Qt.Tool)
            self.rectw, self.recth, self.rectx, self.recty = self.img_toolkit.grep_window()
            point_zero = QtCore.QPoint(self.rectx, self.recty)
            point_one = QtCore.QPoint((self.rectx+self.rectw), (self.recty+self.recth))
            self.cords = QtCore.QRect(point_zero, point_one)
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                                | QtCore.Qt.FramelessWindowHint \
                                | QtCore.Qt.Tool)
            self.showFullScreen()
        self.update()

    def keyReleaseEvent(self, qKeyEvent):
        self.quadratic = False

    def save_image(self, from_dialog=None, clip_only=False, push=True):
        def crop(image):
            rectwidth, rectheight, rectx, recty = (self.sel_rect.width(), 
                                                   self.sel_rect.height(),
                                                   self.sel_rect.x(),
                                                   self.sel_rect.y())
            if "-" in str(rectwidth):
                rectx = rectx + rectwidth
                rectwidth = abs(rectwidth)
            if "-" in str(rectheight):
                recty = recty + rectheight
                rectheight = abs(rectheight)
            image = image.copy(rectx, recty, (rectwidth), (rectheight))
            return image

        if clip_only:
            if self.sel_rect is None:
                self.app.clipboard().setPixmap(self.pixmap())
            else:
                image = self.pixmap().toImage()
                image = crop(image)
                self.app.clipboard().setPixmap(QtGui.QPixmap.fromImage(image))
            return

        image = self.pixmap().toImage()
        # "is not None" because sel_rect can be negative
        if self.sel_rect is not None:
            image = crop(image)
        if not from_dialog:
            image.save(self.filepath)
            if push:
                self.push_to_history(self.filepath, '', 'Save')
        else:
            image.save(from_dialog)
            if push:
                self.push_to_history(from_dialog, '', 'Save')
        # avoid overhead
        if self.config.parse['config']['canvas']['img_clip'] and self.sel_rect is not None:
            self.app.clipboard().setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            self.app.clipboard().setPixmap(self.pixmap())
        self.closeScreen()

    def upload_image(self):
        self.save_image(push=False)

        service = self.config.parse['config']['canvas']['upload_service']
        del_hash = None
        if service == 'Imgur':
            res, del_hash = self.img_toolkit.imgur_upload(self.config, self.filepath, randname=True)
        elif service == 'catbox.moe':
            res = self.img_toolkit.catbox_upload(self.config, self.filepath, randname=True)
        else:
            res = self.img_toolkit.uguu_upload(self.config, self.filepath, randname=True)
        if res.strip():
            self.app.clipboard().setText(res)
        self.push_to_history(self.filepath, res, service, del_hash)

    def push_to_history(self, get_file, response, type_, delete_hash=None):
        curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        thumb = QtGui.QImage(get_file)
        thumb = thumb.scaled(100, 100, Qt.KeepAspectRatioByExpanding,
                                       Qt.SmoothTransformation)
        if thumb.width() > 100:
            rect = QtCore.QRect( 
                (thumb.width() - 100) / 2, 
                (thumb.height() - 100) / 2, 
                100, 
                100, 
            )
            thumb = thumb.copy(rect)

        data = {}
        if not os.path.isdir(self.hist_dir):
            os.mkdir(self.hist_dir)
        if not os.path.isfile(self.hist):
            with open(self.hist, 'w') as file:
                pass
        else:
            with open(self.hist, 'r') as file:
                fdata = file.read()
                if fdata:
                    data = json.loads(fdata)

        if curr_date in data:
            from time import time_ns
            curr_date += ('-'+str(time_ns()))

        thumb_name = os.path.join(self.hist_dir, curr_date+'.png')
        thumb.save(thumb_name)

        if type_ != 'Save':
            type_ = "Upload — "+type_

        data[curr_date] = {
                            "Type":type_,
                            "URL":response,
                            "Path":get_file,
                            "Thumb":thumb_name
                            }
        if delete_hash:
            data[curr_date]['del_hash'] = delete_hash

        with open(self.hist, 'w') as file:
            file.write(str(json.dumps(data)))

        if self.parent.main_window and self.parent.main_window.isVisible():
            item = HistoryItem(self.parent.main_window)
            if delete_hash:
                item.del_hash = delete_hash
            item.date.setText(curr_date)
            item.type.setText(type_)
            if type_ != 'Save':
                item.set_info_url()
                item.info.setText(response)
            else:
                item.set_info_path()
                item.info.setText(get_file)

            item.set_icon(thumb_name)

            widget = QtWidgets.QListWidgetItem()

            widget.setSizeHint(item.sizeHint())

            self.parent.main_window.history_list.insertItem(0, widget)
            self.parent.main_window.history_list.setItemWidget(widget, item)