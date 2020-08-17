#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, QPoint

from PyQt5.QtWidgets import QStylePainter, QStyleOption, QCheckBox, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QFrame, QSlider
from PyQt5.QtWidgets import QPushButton, QGridLayout, QComboBox, QSpinBox
from PyQt5.QtWidgets import QSpacerItem, QWidget, QSizePolicy

def hex_to_rgb(hexv):
    hexv = hexv[1:]
    if not hexv:
        return
    return tuple(int(hexv[i:i+2], 16) for i in (0, 2, 4))

class BaseLayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), \
                                                       __screen_geo.width(), \
                                                       __screen_geo.left(), \
                                                       __screen_geo.top()

        self.setGeometry(0, 0, self.width, self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for i in range(4)]
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

class BaseLayerCanvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), \
                                                       __screen_geo.width(), \
                                                       __screen_geo.left(), \
                                                       __screen_geo.top()

        self.setGeometry(0, 0, self.width, self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for i in range(4)]
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.last_x, self.last_y = None, None

class PenSettingsOutline(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), \
                                                       __screen_geo.width(), \
                                                       __screen_geo.left(), \
                                                       __screen_geo.top()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.setWindowOpacity(0.4)
        widget_width, widget_height = 404, 306
        self.setGeometry(self.parent.pos().x() - 50,
                         self.parent.pos().y() - 122,
                         widget_width, widget_height)

    def resizeEvent(self, event):
        balloon_h = 20
        balloon_w  = 25
        wndRect = self.rect()
        self.wndRect = wndRect
        poly_cords = (
            QPoint(wndRect.x(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),

            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),
            QPoint(wndRect.x() + wndRect.width() / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w / 2, wndRect.height()),
            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w, wndRect.height() - balloon_h),

            QPoint(wndRect.x(), wndRect.height() - balloon_h)
        )
        poly = QtGui.QPolygon(poly_cords)
        mask = QtGui.QRegion(poly)
        self.setMask(mask)

class PenSettings(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), \
                                                       __screen_geo.width(), \
                                                       __screen_geo.left(), \
                                                       __screen_geo.top()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)

        widget_width, widget_height = 400, 300
        self.setGeometry(self.parent.pos().x() - 48,
                         self.parent.pos().y() - 120,
                         widget_width, widget_height)

        self.red = "#c7282e"
        self.yellow = "#dbb126"
        self.green = "#1dc129"
        self.blue = "#3496dd"
        self.white = "#FFFFFF"
        self.black = "#000000"
        self.initUI()
    
    def initUI(self):
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox_left_outer_0 = QHBoxLayout()
        vbox_left_inner = QVBoxLayout()

        qf = QFrame()
        qf.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        two_1 = QHBoxLayout()
        two_2 = QHBoxLayout()
        two_3 = QHBoxLayout()

        lab = QLabel("Foreground color")
        self.red_pen, self.blue_pen, self.green_pen, \
        self.yellow_pen, \
            self.black_pen, self.white_pen = [QPushButton("",
                                              self) for i in range(0, 6)]

        self.btn_css = (
        """
        QPushButton {
            background-color: %s;
            border: 2px solid rgba(0, 0, 0, 0.2);
            margin: 1px;
            padding: 0;
        }

        QPushButton:hover {
            border: 2px solid rgba(0, 0, 0, 0.5);
        }
        """)

        self.btn_css_active = (
        """
        QPushButton {
            background-color: %s;
            border: 2px dashed rgba(0, 0, 0, 0.5);
            margin: 1px;
            padding: 0;
        }

        QPushButton:hover {
            border: 2px solid rgba(0, 0, 0, 0.5);
        }
        """)

        self.red_pen.setStyleSheet(self.btn_css % self.red)
        self.red_pen.clicked.connect(self.red_pen_sel)
        self.blue_pen.setStyleSheet(self.btn_css % self.blue)
        self.blue_pen.clicked.connect(self.blue_pen_sel)
        self.green_pen.setStyleSheet(self.btn_css % self.green)
        self.green_pen.clicked.connect(self.green_pen_sel)
        self.yellow_pen.setStyleSheet(self.btn_css % self.yellow)
        self.yellow_pen.clicked.connect(self.yellow_pen_sel)
        self.black_pen.setStyleSheet(self.btn_css % self.black)
        self.black_pen.clicked.connect(self.black_pen_sel)
        self.white_pen.setStyleSheet(self.btn_css % self.white)
        self.white_pen.clicked.connect(self.white_pen_sel)

        two_1.addWidget(self.red_pen)
        two_1.addWidget(self.blue_pen)
        two_2.addWidget(self.green_pen)
        two_2.addWidget(self.yellow_pen)
        two_3.addWidget(self.black_pen)
        two_3.addWidget(self.white_pen)

        vbox_left_inner.addItem(two_1)
        vbox_left_inner.addItem(two_2)
        vbox_left_inner.addItem(two_3)

        self.pen_op = QSlider()
        self.pen_op.setRange(0, 255)
        self.pen_op.setValue(self.parent.pen_op)
        self.pen_op.valueChanged.connect(self.update_pen_opacity)
        
        hbox_left_inner = QHBoxLayout()
        hbox_left_inner.addItem(vbox_left_inner)
        hbox_left_inner.addWidget(self.pen_op)
        qf.setLayout(hbox_left_inner)

        hbox_left_outer_1 = QHBoxLayout()
        vbox_left_inner_brush = QVBoxLayout()

        qf_brush = QFrame()
        qf_brush.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        two_1_brush = QHBoxLayout()
        two_2_brush = QHBoxLayout()
        two_3_brush = QHBoxLayout()

        lab_brush = QLabel("Background color")
        self.red_brush, self.blue_brush, self.green_brush, \
        self.yellow_brush, \
            self.black_brush, self.white_brush = [QPushButton("",
                                                  self) for i in range(0, 6)]

        self.red_brush.setStyleSheet(self.btn_css % self.red)
        self.red_brush.clicked.connect(self.red_brush_sel)
        self.blue_brush.setStyleSheet(self.btn_css % self.blue)
        self.blue_brush.clicked.connect(self.blue_brush_sel)
        self.green_brush.setStyleSheet(self.btn_css % self.green)
        self.green_brush.clicked.connect(self.green_brush_sel)
        self.yellow_brush.setStyleSheet(self.btn_css % self.yellow)
        self.yellow_brush.clicked.connect(self.yellow_brush_sel)
        self.black_brush.setStyleSheet(self.btn_css % self.black)
        self.black_brush.clicked.connect(self.black_brush_sel)
        self.white_brush.setStyleSheet(self.btn_css % self.white)
        self.white_brush.clicked.connect(self.white_brush_sel)

        two_1_brush.addWidget(self.red_brush)
        two_1_brush.addWidget(self.blue_brush)
        two_2_brush.addWidget(self.green_brush)
        two_2_brush.addWidget(self.yellow_brush)
        two_3_brush.addWidget(self.black_brush)
        two_3_brush.addWidget(self.white_brush)

        vbox_left_inner_brush.addItem(two_1_brush)
        vbox_left_inner_brush.addItem(two_2_brush)
        vbox_left_inner_brush.addItem(two_3_brush)

        self.brush_op = QSlider()
        self.brush_op.setRange(0, 255)
        self.brush_op.setValue(self.parent.brush_op)
        self.brush_op.valueChanged.connect(self.update_brush_opacity)
        
        hbox_brush_inner = QHBoxLayout()
        hbox_brush_inner.addItem(vbox_left_inner_brush)
        hbox_brush_inner.addWidget(self.brush_op)
        qf_brush.setLayout(hbox_brush_inner)

        frame = QVBoxLayout()
        frame.addWidget(lab)
        frame.addWidget(qf)
        frame.addStretch(1)
        frame_brush = QVBoxLayout()
        frame_brush.addWidget(lab_brush)
        frame_brush.addWidget(qf_brush)
        frame_brush.addStretch(1)

        hbox_right = QHBoxLayout()
        hbox_left_outer_0.addItem(frame)
        hbox_left_outer_1.addItem(frame_brush)
        vbox.addItem(hbox_left_outer_0)
        vbox.addItem(hbox_left_outer_1)

        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame().StyledPanel \
                                  | QFrame().Sunken)
        inner_wrap = QVBoxLayout()

        vb_0 = QVBoxLayout()
        vb_1 = QHBoxLayout()
        vb_2 = QHBoxLayout()
        vb_3 = QHBoxLayout()

        pen_size = QLabel("Pen size")
        pen_hbox = QHBoxLayout()

        self.qsl_pen = QSlider(Qt.Horizontal)
        self.qsl_pen.setTickInterval(1)
        self.qsl_pen.setTickPosition(QSlider.TicksAbove)
        self.qsl_pen.setRange(0, 20)
        self.qsl_pen.valueChanged.connect(
            lambda x: self.update_pen_value(self.qsl_pen.value())
        )

        self.qsp = QSpinBox()
        self.qsp.setFixedWidth(46)
        self.qsp.setRange(0, 20)
        self.qsp.valueChanged.connect(
            lambda x: self.update_pen_value(self.qsp.value())
        )

        self.qsl_pen.setValue(self.parent.pen_size)

        pen_hbox.addWidget(self.qsl_pen)
        pen_hbox.addWidget(self.qsp)

        vb_0.addWidget(pen_size)
        vb_0.addItem(pen_hbox)

        line_cap = QLabel("Line cap")
        self.line_qcomb = QComboBox()
        self.line_qcomb.addItem("Square")
        self.line_qcomb.addItem("Round")
        self.line_qcomb.currentIndexChanged.connect(self.update_pen_cap)

        ind = 0
        if self.parent.cap == Qt.RoundCap:
            ind = 1
        self.line_qcomb.setCurrentIndex(ind)

        vb_1.addWidget(line_cap)
        vb_1.addWidget(self.line_qcomb)

        line_joint = QLabel("Line joint style")
        self.line_joint_qcomb = QComboBox()
        self.line_joint_qcomb.addItem("Round")
        self.line_joint_qcomb.addItem("Bevel")
        self.line_joint_qcomb.addItem("Acute")
        self.line_joint_qcomb.currentIndexChanged.connect(self.update_pen_joint)

        ind = 0
        if self.parent.joint == Qt.BevelJoin:
            ind = 1
        elif self.parent.joint == Qt.MiterJoin:
            ind = 2
        self.line_joint_qcomb.setCurrentIndex(ind)

        vb_2.addWidget(line_joint)
        vb_2.addWidget(self.line_joint_qcomb)

        pen_style = QLabel("Line style")
        self.style_qcomb = QComboBox()
        self.style_qcomb.addItem("Solid")
        self.style_qcomb.addItem("Dashed")
        self.style_qcomb.addItem("Dotted")
        self.style_qcomb.addItem("Dash-Dot")
        self.style_qcomb.currentIndexChanged.connect(self.update_pen_style)

        ind = 0
        if self.parent.pen_style == Qt.DashLine:
            ind = 1
        elif self.parent.pen_style == Qt.DotLine:
            ind = 2
        elif self.parent.pen_style == Qt.DashDotLine:
            ind = 3
        self.style_qcomb.setCurrentIndex(ind)

        vb_3.addWidget(pen_style)
        vb_3.addWidget(self.style_qcomb)

        vb_4 = QHBoxLayout()
        out_lab = QLabel("Outline")
        self.outline = QComboBox()
        self.outline.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.outline.addItem("Disabled")
        self.outline.addItem("Black")
        self.outline.addItem("Background")
        curr_out = self.parent.config.parse['config']['canvas']['outline']
        if curr_out == 'black':
            self.outline.setCurrentIndex(1)
        elif curr_out == 'background':
            self.outline.setCurrentIndex(2)
        self.outline.currentIndexChanged.connect(self.update_outline)
        vb_4.addWidget(out_lab)
        vb_4.addWidget(self.outline)

        inner_wrap.addItem(vb_0)
        inner_wrap.addItem(vb_1)
        inner_wrap.addItem(vb_2)
        inner_wrap.addItem(vb_3)
        inner_wrap.addItem(vb_4)
        inner_wrap.addStretch(1)

        right_frame.setLayout(inner_wrap)
        right_wrap = QVBoxLayout()
        right_wrap.addWidget(right_frame)
        hbox_right.addItem(right_wrap)

        vbox.addStretch(1)
        vbox_vert = QVBoxLayout()
        vbox_q = QWidget()
        vbox_q.setLayout(vbox)
        vbox_q.setFixedWidth(140)
        hbox_q = QWidget()
        hbox_q.setLayout(hbox_right)

        hbox.addWidget(vbox_q)
        hbox.addWidget(hbox_q)

        vbox_vert.addItem(hbox)
        vbox_vert.addStretch(1)
        self.setStyleSheet("QFrame { margin: 2px; }")
        self.setLayout(vbox_vert)

    def update_pen_opacity(self):
        self.parent.pen_op = self.pen_op.value()
        self.parent.update_pen_color()
        self.parent.config.changeConfig("canvas", "pen_opacity", self.pen_op.value())

    def update_brush_opacity(self):
        self.parent.brush_op = self.brush_op.value()
        self.parent.update_brush_color()
        self.parent.config.changeConfig("canvas", "brush_opacity", self.brush_op.value())

    def update_pen_style(self):
        ind = self.style_qcomb.currentIndex()
        styles = ["solid", "dash", "dot", "dashdot"]

        if ind == 0:
            self.parent.pen_style = Qt.SolidLine
        elif ind == 1:
            self.parent.pen_style = Qt.DashLine
        elif ind == 2:
            self.parent.pen_style = Qt.DotLine
        else:
            self.parent.pen_style = Qt.DashDotLine
        
        self.parent.config.changeConfig("canvas", "last_style", styles[ind])

    def update_pen_value(self, value):
        if type(value) is int:
            self.qsl_pen.setValue(value)
            self.qsp.setValue(value)
            self.parent.pen_size = value

            self.parent.config.changeConfig("canvas", "last_size", value)

    def update_pen_cap(self):
        ind = self.line_qcomb.currentIndex()
        caps = ["square", "round"]
        if ind == 0:
            self.parent.cap = Qt.SquareCap
        else:
            self.parent.cap = Qt.RoundCap
        
        self.parent.config.changeConfig("canvas", "last_cap", caps[ind])

    def update_outline(self):
        self.parent.config.changeConfig('canvas', 'outline', self.outline.currentText().lower())

    def update_pen_joint(self):
        ind = self.line_joint_qcomb.currentIndex()
        joints = ["round", "bevel", "miter"]
        if ind == 0:
            self.parent.joint = Qt.RoundJoin
        elif ind == 1:
            self.parent.joint = Qt.BevelJoin
        else:
            self.parent.joint = Qt.MiterJoin

        self.parent.config.changeConfig("canvas", "last_joint", joints[ind])

    def closeEvent(self, event):
        self.setWindowOpacity(0)
        self.close()

    def resizeEvent(self, event):
        balloon_h = 20
        balloon_w = 25
        wndRect = self.rect()
        self.wndRect = wndRect
        # https://github.com/sharkpp/qtpopover
        poly_cords = (
            QPoint(wndRect.x(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),

            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),
            QPoint(wndRect.x() + wndRect.width() / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w / 2, wndRect.height()),
            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w, wndRect.height() - balloon_h),

            QPoint(wndRect.x(), wndRect.height() - balloon_h)
        )
        poly = QtGui.QPolygon(poly_cords)
        mask = QtGui.QRegion(poly)
        self.setMask(mask)

    def reset_pen_btn_css(self):
        self.red_pen.setStyleSheet(self.btn_css % self.red)
        self.blue_pen.setStyleSheet(self.btn_css % self.blue)
        self.green_pen.setStyleSheet(self.btn_css % self.green)
        self.yellow_pen.setStyleSheet(self.btn_css % self.yellow)
        self.black_pen.setStyleSheet(self.btn_css % self.black)
        self.white_pen.setStyleSheet(self.btn_css % self.white)

    def reset_brush_btn_css(self):
        self.red_brush.setStyleSheet(self.btn_css % self.red)
        self.blue_brush.setStyleSheet(self.btn_css % self.blue)
        self.green_brush.setStyleSheet(self.btn_css % self.green)
        self.yellow_brush.setStyleSheet(self.btn_css % self.yellow)
        self.black_brush.setStyleSheet(self.btn_css % self.black)
        self.white_brush.setStyleSheet(self.btn_css % self.white)

    @QtCore.pyqtSlot()
    def red_pen_sel(self):
        self.reset_pen_btn_css()
        self.red_pen.setStyleSheet(self.btn_css_active % self.red)
        self.parent.current_pen_color = hex_to_rgb(self.red)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.red)
        self.parent.update_pen_color()
    def blue_pen_sel(self):
        self.reset_pen_btn_css()
        self.blue_pen.setStyleSheet(self.btn_css_active % self.blue)
        self.parent.current_pen_color = hex_to_rgb(self.blue)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.blue)
        self.parent.update_pen_color()
    def green_pen_sel(self):
        self.reset_pen_btn_css()
        self.green_pen.setStyleSheet(self.btn_css_active % self.green)
        self.parent.current_pen_color = hex_to_rgb(self.green)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.green)
        self.parent.update_pen_color()
    def yellow_pen_sel(self):
        self.reset_pen_btn_css()
        self.yellow_pen.setStyleSheet(self.btn_css_active % self.yellow)
        self.parent.current_pen_color = hex_to_rgb(self.yellow)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.yellow)
        self.parent.update_pen_color()
    def black_pen_sel(self):
        self.reset_pen_btn_css()
        self.black_pen.setStyleSheet(self.btn_css_active % self.black)
        self.parent.current_pen_color = hex_to_rgb(self.black)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.black)
        self.parent.update_pen_color()
    def white_pen_sel(self):
        self.reset_pen_btn_css()
        self.white_pen.setStyleSheet(self.btn_css_active % self.white)
        self.parent.current_pen_color = hex_to_rgb(self.white)
        self.parent.config.changeConfig("canvas", "last_pen_color", self.white)
        self.parent.update_pen_color()

    def red_brush_sel(self):
        self.reset_brush_btn_css()
        self.red_brush.setStyleSheet(self.btn_css_active % self.red)
        self.parent.current_brush_color = hex_to_rgb(self.red)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.red) 
        self.parent.update_brush_color()
    def blue_brush_sel(self):
        self.reset_brush_btn_css()
        self.blue_brush.setStyleSheet(self.btn_css_active % self.blue)
        self.parent.current_brush_color = hex_to_rgb(self.blue)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.blue)
        self.parent.update_brush_color()
    def green_brush_sel(self):
        self.reset_brush_btn_css()
        self.green_brush.setStyleSheet(self.btn_css_active % self.green)
        self.parent.current_brush_color = hex_to_rgb(self.green)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.green)
        self.parent.update_brush_color()
    def yellow_brush_sel(self):
        self.reset_brush_btn_css()
        self.yellow_brush.setStyleSheet(self.btn_css_active % self.yellow)
        self.parent.current_brush_color = hex_to_rgb(self.yellow)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.yellow)
        self.parent.update_brush_color()
    def black_brush_sel(self):
        self.reset_brush_btn_css()
        self.black_brush.setStyleSheet(self.btn_css_active % self.black)
        self.parent.current_brush_color = hex_to_rgb(self.black)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.black)
        self.parent.update_brush_color()
    def white_brush_sel(self):
        self.reset_brush_btn_css()
        self.white_brush.setStyleSheet(self.btn_css_active % self.white)
        self.parent.current_brush_color = hex_to_rgb(self.white)
        self.parent.config.changeConfig("canvas", "last_brush_color", self.white)
        self.parent.update_brush_color()

class Toolkit(BaseLayer):
    def __init__(self, parent, config):
        super().__init__()
        self.config = config
        self.parent = parent

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        widget_width, widget_height = 280, 300
        self.setGeometry((self.left + (self.width / 2 - 150)),
                         (self.top + (self.height - 300)),
                         widget_width, widget_height)

        self.switch = 0

        self.pen_op = self.config.parse["config"]["canvas"]["pen_opacity"]
        self.brush_op = self.config.parse["config"]["canvas"]["brush_opacity"]

        self.brush_selection_color = QtGui.QColor(103, 150, 188, 40)
        self.pen_selection_color = QtGui.QColor(103, 150, 188, 100)

        _pen = self.config.parse["config"]["canvas"]["last_pen_color"]
        _brush = self.config.parse["config"]["canvas"]["last_brush_color"]

        self.current_pen_color = hex_to_rgb("#c7282e") if not _pen else hex_to_rgb(_pen)
        self.current_brush_color = hex_to_rgb("#c7282e") if not _brush else hex_to_rgb(_brush)

        self.update_pen_color()
        self.update_brush_color()

        self.pen_size = self.config.parse["config"]["canvas"]["last_size"]

        styles = [["solid", Qt.SolidLine], ["dash", Qt.DashLine],
                  ["dot", Qt.DotLine], ["dashdot", Qt.DashDotLine]]

        caps = [["square", Qt.SquareCap], ["round", Qt.RoundCap]]

        joints = [["round", Qt.RoundJoin],
                  ["bevel", Qt.RoundJoin],
                  ["miter", Qt.MiterJoin]]

        style = self.config.parse["config"]["canvas"]["last_style"]
        for s in styles:
            if style == s[0]:
                self.pen_style = s[1]
        
        joint = self.config.parse["config"]["canvas"]["last_joint"]
        for j in joints:
            if joint == j[0]:
                self.joint = j[1]
        
        cap = self.config.parse["config"]["canvas"]["last_cap"]
        for c in caps:
            if cap == c[0]:
                self.cap = c[1]

        self.pens = PenSettings(self)
        self.pens_outline = PenSettingsOutline(self)
        if not _brush:
            self.pens.red_brush_sel()
        else:
            if _brush == self.pens.red:
                self.pens.red_brush_sel()
            elif _brush == self.pens.yellow:
                self.pens.yellow_brush_sel()
            elif _brush == self.pens.blue:
                self.pens.blue_brush_sel()
            elif _brush == self.pens.green:
                self.pens.green_brush_sel()
            elif _brush == self.pens.black:
                self.pens.black_brush_sel()
            else:
                self.pens.white_brush_sel()
        if not _pen:
            self.pens.red_pen_sel()
        else:
            if _pen == self.pens.red:
                self.pens.red_pen_sel()
            elif _pen == self.pens.yellow:
                self.pens.yellow_pen_sel()
            elif _pen == self.pens.blue:
                self.pens.blue_pen_sel()
            elif _pen == self.pens.green:
                self.pens.green_pen_sel()
            elif _pen == self.pens.black:
                self.pens.black_pen_sel()
            else:
                self.pens.white_pen_sel()
        self.initUI()

    def initUI(self):
        grid = QGridLayout(self)

        self.select, self.rectangle, self.line, \
            self.pen_btn, self.circle, self.close_btn, \
                self.free_btn, self.color, \
                    self.save, self.upload = [QPushButton() for i in range(10)]

        btn_css = (
        """
        QPushButton {
            qproperty-icon: url(" ");
            qproperty-iconSize: 64px 64px;
            background-image: url(%s/img/%s.png);
            background-repeat: no-repeat;
            border: 0;
            margin: 0;
            padding: 0;
            background-position: center;
        }

        QPushButton:hover {
            background-image: url(%s/img/%s.png);
            background-repeat: no-repeat;
            background-position: center;
        }
        """)

        #close_css = btn_css.replace('64px', '32px')

        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(8)
        self.setLayout(grid)

        self.btn_css = {
            "pen": "",
            "free": "",
            "sel": "",
            "rect": "",
            "line": "",
            "circle": "",
            "close": "",
            "save": "",
            "upload": "",
            "color": ""
        }
        self.btn_css_active = {x:"" for x in self.btn_css.keys()}
        for key in self.btn_css:
            self.btn_css[key] = btn_css % (sys.path[0], key, sys.path[0],
                                                            key+'_hover')
        for key in self.btn_css_active:
            self.btn_css_active[key] = btn_css % (sys.path[0], key+'_hover',
                                                  sys.path[0], key+'_hover')

        self.free_btn.clicked.connect(self.free_selected)
        self.free_btn.setStyleSheet(self.btn_css['free'])
        self.free_btn.setToolTip("Free shape tool")

        self.color.clicked.connect(self.color_selected)
        self.color.setStyleSheet(self.btn_css['color'])
        self.color.setToolTip("Paint settings")

        self.select.clicked.connect(self.selected)
        self.select.setStyleSheet(self.btn_css['sel'])
        self.select.setToolTip("Selection")

        self.rectangle.clicked.connect(self.rect_selected)
        self.rectangle.setStyleSheet(self.btn_css['rect'])
        self.rectangle.setToolTip("Rectangle tool")

        self.line.clicked.connect(self.line_selected)
        self.line.setStyleSheet(self.btn_css['line'])
        self.line.setToolTip("Line tool")

        self.pen_btn.clicked.connect(self.pen_selected)
        self.pen_btn.setStyleSheet(self.btn_css['pen'])
        self.pen_btn.setToolTip("Pen tool")

        self.circle.clicked.connect(self.circle_selected)
        self.circle.setStyleSheet(self.btn_css['circle'])
        self.circle.setToolTip("Circle tool")

        self.close_btn.clicked.connect(self.close_clicked)
        self.close_btn.setStyleSheet(self.btn_css['close'])
        self.close_btn.setToolTip("Cancel")

        self.save.setStyleSheet(self.btn_css['save'])
        self.save.setToolTip("Save")
        self.save.clicked.connect(self.save_action)
        self.upload.setStyleSheet(self.btn_css['upload'])
        self.upload.setToolTip("Upload")
        self.upload.clicked.connect(self.parent.upload_image)

        vspace = QSpacerItem(0, 0, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding)
 
        grid.addWidget(self.save, 0, 0)
        grid.addWidget(self.upload, 0, 1)
        grid.addWidget(self.close_btn, 0, 2)
        grid.addWidget(self.select, 1, 1)
        grid.addWidget(self.pen_btn, 2, 0)
        grid.addWidget(self.color, 2, 1)
        grid.addWidget(self.free_btn, 2, 2)
        grid.addWidget(self.rectangle, 3, 0)
        grid.addWidget(self.circle, 3, 1)
        grid.addWidget(self.line, 3, 2)
        grid.addItem(vspace, 4, 0, 1, -1)

    def closeEvent(self, event):
        self.pens_outline.setWindowOpacity(0)
        self.pens_outline.close()
        self.pens.setWindowOpacity(0)
        self.pens.close()
        self.setWindowOpacity(0)
        self.close()

    def close_clicked(self):
        self.close()
        self.parent.close()

    def showEvent(self, event):
        self.show()
        self.setWindowOpacity(1)
        self.redefine_css()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.close()

    def save_action(self):
        if self.config.parse['config']['canvas']['save_action'] == 'dir':
            self.parent.save_image()
            return
        qdialog_filter = 'Pictures (*.png *.jpg *.jpeg *.bmp *.ico *.tiff)'
        filedial = QtWidgets.QFileDialog()
        filedial.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.close()
        fd = filedial.getSaveFileName(self, "Save to", '', qdialog_filter)
        filepath = fd[0] if fd[0] else None
        if filepath:
            if not filepath.endswith('.png'):
                filepath += '.png'
            self.parent.save_image(filepath)

    def update_pen_color(self):
        self.pen_color = QtGui.QColor(*self.current_pen_color, self.pen_op)

    def update_brush_color(self):
        self.brush_color = QtGui.QColor(*self.current_brush_color, self.brush_op)

    def redefine_css(self):
        if self.switch == 5:
            self.free_selected()
        elif self.switch == 4:
            self.line_selected()
        elif self.switch == 3:
            self.rect_selected()
        elif self.switch == 2:
            self.circle_selected()
        elif self.switch == 1:
            self.pen_selected()
        else:
            self.selected()

    def reset_css(self, check=True):
        if check:
            self.check_color()
        self.line.setStyleSheet(self.btn_css['line'])
        self.rectangle.setStyleSheet(self.btn_css['rect'])
        self.circle.setStyleSheet(self.btn_css['circle'])
        self.pen_btn.setStyleSheet(self.btn_css['pen'])
        self.select.setStyleSheet(self.btn_css['sel'])
        self.free_btn.setStyleSheet(self.btn_css['free'])
        self.color.setStyleSheet(self.btn_css['color'])

    @QtCore.pyqtSlot()
    def color_selected(self):
        self.reset_css(check=False)
        if self.pens.isVisible():
            self.color.setStyleSheet(self.btn_css['color'])
            self.pens_outline.setWindowOpacity(0)
            self.pens.close()
            self.pens_outline.close()
            self.redefine_css()
        else:
            self.color.setStyleSheet(self.btn_css_active['color'])
            self.pens_outline.setWindowOpacity(0)
            self.pens_outline.setStyleSheet("background: #131313;")
            self.pens_outline.show()
            self.pens_outline.setWindowOpacity(0.6)
            self.pens.setWindowOpacity(1)
            self.pens.show()
            self.pens_outline.raise_()
            self.pens.raise_()

    def check_color(self):
        if self.pens.isVisible():
            self.color.setStyleSheet(self.btn_css['color'])
            self.pens_outline.setWindowOpacity(0)
            self.pens.close()
            self.pens_outline.close()

    def free_selected(self):
        self.reset_css()
        self.free_btn.setStyleSheet(self.btn_css_active['free'])
        self.switch = 5
    def line_selected(self):
        self.reset_css()
        self.line.setStyleSheet(self.btn_css_active['line'])
        self.switch = 4
    def rect_selected(self):
        self.reset_css()
        self.rectangle.setStyleSheet(self.btn_css_active['rect'])
        self.switch = 3
    def circle_selected(self):
        self.reset_css()
        self.circle.setStyleSheet(self.btn_css_active['circle'])
        self.switch = 2
    def pen_selected(self):
        self.reset_css()
        self.pen_btn.setStyleSheet(self.btn_css_active['pen'])
        self.switch = 1
    def selected(self):
        self.reset_css()
        self.select.setStyleSheet(self.btn_css_active['sel'])
        self.switch = 0