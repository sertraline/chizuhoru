from screenshot import ScreenshotCLI
from PyQt5.QtGui import QPainter, QImage, QPalette, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, QPoint
from PyQt5 import QtCore

from datetime import datetime
import json
import sys
import os
import gc

import qt_toolkit
from main_window import HistoryItem

import ctypes
import sip
try:
    qtgui = ctypes.CDLL('libQt5Widgets.so')
except:
    qtgui = ctypes.CDLL('libQt5Widgets.so.5')
_qt_blurImage = qtgui._Z12qt_blurImageP8QPainterR6QImagedbbi

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)

    def __init__(self, fn, args, _type):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.type = _type

    @QtCore.pyqtSlot()
    def run(self):
        if self.type == 'Imgur':
            try:
                ret_val, del_hash = self.fn(*self.args)
            except (ValueError, TypeError):
                self.finished.emit([])
                return
            self.finished.emit([self.args[1], ret_val, del_hash])
        else:
            ret_val = self.fn(*self.args)
            self.finished.emit([self.args[1], ret_val, None])

class EventHistory:
    def __init__(self):
        self.pen = []
        self.rect = []
        self.circle = []
        self.line = []
        self.free = []
        self.blur = []

        # string takes less memory than a list
        self.sequence = ''

class ScreenWindow(qt_toolkit.BaseLayerCanvas):

    def __init__(self, parent, app, config, image_toolkit, fallback):
        super().__init__()

        self.parent = parent
        self.app = app
        self.config = config
        self.screen_unit = ScreenshotCLI()
        self.thread = None

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
        self.pixel_data = None

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.Tool)
        self.setMouseTracking(True)

        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setStyleSheet("border: 6px solid rgba(0, 0, 0, 60);")
        self.pixel_info = QtWidgets.QWidget(self)

        self.pixel_info.setFixedSize(128, 24)
        self.pixel_info_label = QtWidgets.QLabel()
        _font = QtGui.QFont()
        _font.setPointSize(8)
        self.pixel_info_label.setFont(_font)
        _l = QtWidgets.QHBoxLayout()
        _l.addWidget(self.pixel_info_label)
        self.pixel_info.setLayout(_l)

        self.cursor = None
        self.scene_px = None

        # define image processing methods separated from GUI
        self.img_toolkit = image_toolkit
        # define right-click control menu
        self.toolkit = qt_toolkit.Toolkit(self, self.config, fallback)
        self.toolkit.setMouseTracking(True)

        self.showFullScreen()
        self.render_background()

        self.view.setFixedSize(140, 140)
        self.cursor = self.scene.addPixmap(QtGui.QPixmap(f"{sys.path[0]}/img/pixel.png"))
        self.cursor.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
        self.cursor.setPos(0, 0)

        brush = QBrush(QtGui.QPixmap(f"{sys.path[0]}/img/grid.png"))
        self.scene.setBackgroundBrush(brush)

        borderColor = QtGui.QColor('black')
        rect = QtCore.QRectF(0, 0, self.width*10, self.height*10)

        x = self.scene.addRect(rect,borderColor,brush)
        x.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

        self.view.move(self.width - 200, 40)
        self.pixel_info.move(self.view.pos().x()+6, self.view.pos().y()+6)
        self.pixel_info.setStyleSheet('background-color: rgba(0, 0, 0, 80);')
        self.pixel_info_label.setStyleSheet('background-color: transparent; margin:0; padding:0;')
        self.pixel_info.show()
        self.view.setSceneRect(0, 0, 140, 140)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # RightMouseButton -> paint_allowed = False
        # LeftMouseButton  -> paint_allowed = True
        self.paint_allowed = False
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

        self.view.show()
        _pen = QtGui.QPen(QtGui.QColor(103, 150, 188, 180), 0.6, Qt.SolidLine, Qt.SquareCap)
        _brush = QtGui.QBrush(self.toolkit.brush_selection_color)
        self.scene_sel = self.scene.addRect(QtCore.QRectF(0, 0, 0, 0), _pen, _brush)

    def render_background(self):
        qimg = QtGui.QPixmap()
        qimg.loadFromData(self.temp.getvalue())
        self.setPixmap(qimg)
        self.pixel_data = QImage()
        self.pixel_data.loadFromData(self.temp.getvalue())
        if not self.scene_px:
            self.scene_px = self.scene.addPixmap(qimg)
            self.view.scale(8, 8)

    def paintEvent(self, event):
        super(ScreenWindow, self).paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        brush, pen, pen_outline = self.get_drawing_pen()
        sel_pen = QtGui.QPen(self.toolkit.pen_selection_color, 2, Qt.DashLine)
        sel_brush = QtGui.QBrush(self.toolkit.brush_selection_color)

        painter.setPen(pen)
        painter.setBrush(brush)

        if not self.cords:
            rect = self.build_rect()

            # if paint tool is selected and LMB clicked, process event
            if self.paint_allowed:
                # switch 1: pen drawing, switch 5: free drawing
                if self.toolkit.switch == 5:
                    if not self.pen_point_list:
                        return
                    self.build_path()
                    if not self.path:
                        return

                    if pen_outline:
                        painter.setPen(pen_outline)
                        painter.drawPath(self.path)
                        painter.setPen(pen)
                    painter.drawPath(self.path)
                elif self.toolkit.switch == 2:
                    if pen_outline:
                        painter.setPen(pen_outline)
                        painter.drawEllipse(rect)
                        painter.setPen(pen)
                    painter.drawEllipse(rect)
                elif self.toolkit.switch == 3:
                    painter.drawRect(rect)
                elif self.toolkit.switch == 4:
                    painter.drawLine(self.begin.x(), self.begin.y(),
                                     self.end.x(), self.end.y())
                else:
                    # switch 0: selection, switch 6: blur
                    painter.setPen(sel_pen)
                    painter.setBrush(sel_brush)
                    if self.begin != self.end:
                        painter.drawRect(rect)
                        self.sel_rect = rect
            else:
                # redraw last selection rectangle on RMB click
                if self.sel_rect is not None:
                    painter.setPen(sel_pen)
                    painter.setBrush(sel_brush)
                    painter.drawRect(self.sel_rect)
        else:
            painter.setPen(sel_pen)
            painter.setBrush(sel_brush)
            painter.drawRect(self.cords)
            self.sel_rect = self.cords
            self.cords = None

    def closeScreen(self):
        self.toolkit.close()
        self.temp = None
        self.pixel_data = QImage()
        gc.collect()
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
            self.scene_sel.setRect(0, 0, 0, 0)

            if self.toolkit.switch == 5:
                self.pen_point_list = []
            elif self.toolkit.switch == 1:
                self.last_x = event.x()
                self.last_y = event.y()
            self.begin = event.pos()
            self.end = event.pos()

            cases = [0, 6, 4, 3, 2]
            if any(self.toolkit.switch == x for x in cases) and self.scene_sel:
                x, y = self.begin.x(), self.begin.y()
                width, height = self.end.x()-self.begin.x(), \
                                self.end.y()-self.begin.y()

                self.scene_sel.setRect(x, y, width, height)
            self.update()

    def mouseMoveEvent(self, event):
        self.view.setSceneRect(
            (event.x())-70,
            (event.y())-70,
            140, 140
        )
        self.view.centerOn(event.x(), event.y())
        self.cursor.setPos((event.x()-8),
                           (event.y()-8))

        _px = self.pixel_data.pixel(event.x(), event.y())
        _px = QtGui.QColor(_px).getRgb()
        _px = _px[:-1]
        _info = '#{:02x}{:02x}{:02x}'.format(*_px)
        _cords = f'{event.x()}, {event.y()}'
        self.pixel_info_label.setText(f'{_info:<8} {_cords:>7}')

        xpos = event.x()-70
        ypos = event.y()+20
        if (event.x()-70 < 0):
            xpos = event.x()
        if (event.x()+70 > self.width):
            xpos = event.x()-140
        if (event.y()+170 > self.height):
            ypos = event.y() - 170

        if self.toolkit.isVisible():
            wstart = self.toolkit.pos().x()
            ystart = self.toolkit.pos().y() - 35
            wend = self.toolkit.pos().x() + self.toolkit.geometry().width()
            yend = self.toolkit.pos().y() + self.toolkit.geometry().height()
            if (event.y() >= ystart and event.y() <= yend) and \
                (event.x() >= wstart-70 and event.x() <= wend+70):
                ypos = ystart - 200

        self.view.move(xpos, ypos)
        self.pixel_info.move(self.view.pos().x()+6, self.view.pos().y()+6)
        self.update()

        # switch 1: pen drawing, switch 5: free drawing
        if (self.toolkit.switch == 1 or self.toolkit.switch == 5) \
            and event.buttons() == QtCore.Qt.LeftButton:
            if self.last_x is None:
                self.last_x = event.x()
                self.last_y = event.y()
                return

            painter = QPainter(self.pixmap())
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setPen(QtGui.QPen(self.toolkit.pen_color,
                                      self.toolkit.pen_size))

            pen = QtGui.QPen(self.toolkit.pen_color, self.toolkit.pen_size,
                             self.toolkit.pen_style, self.toolkit.cap, self.toolkit.joint)
            brush = QtGui.QBrush(self.toolkit.brush_color)
            painter.setBrush(brush)
            painter.setPen(pen)

            if self.toolkit.switch == 5:
                self.last_x = event.x()
                self.last_y = event.y()
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

            # don't display selection for tools not in list
            cases = [0, 6, 4, 3, 2]
            if any(self.toolkit.switch == x for x in cases) and self.scene_sel:
                x, y = self.begin.x(), self.begin.y()
                width, height = self.end.x()-self.begin.x(), \
                                self.end.y()-self.begin.y()

                if self.quadratic:
                    rect = self.rect_quadratic(QtCore.QRect(x, y, width, height))
                    x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()

                self.scene_sel.setRect(x+0.4, y+0.4, width, height)
            self.update()

    def build_rect(self):
        rect = QtCore.QRect(self.begin, self.end)
        if self.quadratic:
            rect = self.rect_quadratic(rect)

        x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()

        # fix coordinates misalignment
        width -= 1
        height -= 1

        rect = QtCore.QRect(x, y, width, height)
        return rect

    def build_path(self):
        factor = 0.4
        points = self.pen_point_list
        self.path = QtGui.QPainterPath(points[0])
        cp1 = None
        if len(points) > 6:
            # throw away excess points to make curve smoother
            points = points[::5]

            for count, point in enumerate(points):
                if count < 1 or not points[count-1]:
                    continue
                if abs(point.x() - points[count-1].x()
                    ) < 10 or abs(point.y() - points[count-1].y()) < 10:
                    check_points = [x for x in points if x]
                    if len(check_points) > 4:
                        points[count] = None

        points = [x for x in points if x]
        if len(points) < 3:
            for point in points:
                self.path.lineTo(point.x(), point.y())
            return

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
                continue

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

    def ctypes_blur(self, p, dest_img, radius, quality, alphaOnly, transposed=0):
        p = ctypes.c_void_p(sip.unwrapinstance(p))
        dest_img = ctypes.c_void_p(sip.unwrapinstance(dest_img))
        radius = ctypes.c_double(radius)
        quality = ctypes.c_bool(quality)
        alphaOnly = ctypes.c_bool(alphaOnly)
        transposed = ctypes.c_int(transposed)
        _qt_blurImage(p, dest_img, radius, quality, alphaOnly, transposed)

    def get_drawing_pen(self):
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
        return brush, pen, pen_outline

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

        if self.toolkit.switch == 0 and self.sel_rect \
            and event.buttons() == QtCore.Qt.LeftButton:
            self.scene_sel.setRect(self.begin.x(), self.begin.y(),
                                    self.end.x()-self.begin.x(),
                                    self.end.y()-self.begin.y())
            self.paint_allowed = False
        elif self.toolkit.switch == 0:
            self.paint_allowed = False
        if not self.paint_allowed:
            return

        self.paint_allowed = False

        if self.begin == self.end:
            return

        if self.toolkit.switch == 6:
            self.scene_sel.setRect(self.begin.x(), self.begin.y(),
                                    self.end.x()-self.begin.x(),
                                    self.end.y()-self.begin.y())
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

            tmp = self.crop(self.pixmap().toImage())

            blurred = QtGui.QImage(tmp.size(),
                                   QtGui.QImage.Format_ARGB32_Premultiplied)
            blurred.fill(QtGui.QColor('transparent'))
            painter = QPainter(blurred)

            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setRenderHint(QPainter.LosslessImageRendering)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            self.ctypes_blur(painter, tmp, 45, True, False)
            painter.end()

            dest = QtGui.QPixmap().fromImage(blurred)
            
            painter = QPainter(self.pixmap())
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            self.history.sequence += 'b'
            for i in range(6):
                painter.drawPixmap(rectx, recty, rectwidth, rectheight, dest)
            self.history.blur.append([rectx, recty, rectwidth, rectheight, dest])
            painter.end()
            self.update()

            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            self.sel_rect = None
            self.scene_sel.setRect(0, 0, 0, 0)
            self.scene_px.setPixmap(self.pixmap())
            self.pixel_data = self.pixmap().toImage()
            return

        painter = QPainter(self.pixmap())
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        brush, pen, pen_outline = self.get_drawing_pen()

        painter.setBrush(brush)
        painter.setPen(pen)

        rect = self.build_rect()

        if self.toolkit.switch == 5:
            self.build_path()
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
            self.scene_px.setPixmap(self.pixmap())
            self.pixel_data = self.pixmap().toImage()
            self.update()
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
        
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.scene_px.setPixmap(self.pixmap())
        self.pixel_data = self.pixmap().toImage()
        self.update()

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
           ) and (qKeyEvent.nativeScanCode() == 52):
            if len(self.history.sequence) == 0:
                return

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
            blur_cnt = -1
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
                elif item == 'b':
                    blur_cnt += 1
                    args = self.history.blur[blur_cnt]
                    for i in range(6):
                        painter.drawPixmap(*args)

            last_item = self.history.sequence[-1]
            items = [['p', self.history.pen],
                     ['r', self.history.rect],
                     ['l', self.history.line],
                     ['f', self.history.free],
                     ['b', self.history.blur],
                     ['c', self.history.circle]]
            for item in items:
                if last_item == item[0]:
                    item[1].pop(-1)

            self.history.sequence = self.history.sequence[:-1]
            painter.end()
            self.scene_px.setPixmap(self.pixmap())
            self.pixel_data = self.pixmap().toImage()
            return

        elif qKeyEvent.key() == QtCore.Qt.Key_Return:
            self.save_image(clip_only=True)
            self.closeScreen()

        elif qKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.closeScreen()

        elif qKeyEvent.nativeScanCode() >= 10 and qKeyEvent.nativeScanCode() <= 16:
            for key in self.toolkit.switches:
                if qKeyEvent.nativeScanCode() == key[1]+10:
                    self.toolkit.tool_sel(key[0])
                    return

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
        
        elif qKeyEvent.nativeScanCode() == 52: #"Z"
            if self.view.isVisible():
                self.pixel_info.hide()
                self.view.hide()
            else:
                self.pixel_info.show()
                self.view.show()
        self.update()

    def keyReleaseEvent(self, qKeyEvent):
        self.quadratic = False

    def crop(self, image):
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
        rectwidth += 1
        rectheight += 1
        image = image.copy(rectx, recty, (rectwidth), (rectheight))
        return image

    def save_image(self, from_dialog=None, clip_only=False, push=True):
        if clip_only:
            if self.sel_rect is None:
                self.app.clipboard().setPixmap(self.pixmap())
            else:
                image = self.pixmap().toImage()
                image = self.crop(image)
                self.app.clipboard().setPixmap(QtGui.QPixmap.fromImage(image))
            return

        image = self.pixmap().toImage()
        # "is not None" because sel_rect can be negative
        if self.sel_rect is not None:
            image = self.crop(image)
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
        if push:
            self.closeScreen()

    def upload_image(self):
        service = self.config.parse['config']['canvas']['upload_service']
        del_hash = None

        args = [self.config, self.filepath, True]

        if service == 'Imgur':
            self.worker = Worker(self.img_toolkit.imgur_upload, args, 'Imgur')
        elif service == 'catbox.moe':
            self.worker = Worker(self.img_toolkit.catbox_upload, args, 'catbox.moe')
        else:
            self.worker = Worker(self.img_toolkit.uguu_upload, args, 'uguu.se')

        self.thread = QtCore.QThread()
        self.worker.finished.connect(self.get_ret_val)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        self.save_image(push=False)

        self.thread.start()
        self.toolkit.hide()
        self.hide()

    def get_ret_val(self, response):
        if response:
            filename = response[0]
            del_hash = response[2]
            response = response[1]
            type_ = self.config.parse['config']['canvas']['upload_service']
            self.push_to_history(filename, response, type_, del_hash)
            self.app.clipboard().setText(response)
            cmd = ("""
            gdbus call --session \
            --dest org.freedesktop.Notifications \
            --object-path /org/freedesktop/Notifications \
            --method org.freedesktop.Notifications.Notify \
            'Chizuhoru' 0 dialog-information "Upload %s" "%s" [] {} 3000
            """ % (type_, response))
            os.popen(cmd)
        self.thread.quit()
        self.temp = None
        self.pixel_data = QImage()
        gc.collect()
        self.deleteLater()
        self.close()

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

        thumb_name = os.path.join(self.hist_dir, 'thumb_'+curr_date+'.png')
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
