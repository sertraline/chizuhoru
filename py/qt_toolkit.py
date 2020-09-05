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
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.last_x, self.last_y = None, None

class ToolsConfigOutline(QtWidgets.QDialog):
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
        self.setFixedSize(widget_width, widget_height)
        self.setGeometry((self.width/2) - (widget_width/2),
                         self.parent.pos().y() - 124,
                         widget_width, widget_height)

    def resizeEvent(self, event):
        balloon_h = 20
        balloon_w  = 30
        wndRect = self.rect()
        self.wndRect = wndRect
        # https://github.com/sharkpp/qtpopover
        poly_cords = (
            QPoint(wndRect.x(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),

            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),
            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width() / 2, wndRect.height()),
            QPoint(wndRect.x() + wndRect.width() / 2 + balloon_w / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x(), wndRect.height() - balloon_h)
        )
        poly = QtGui.QPolygon(poly_cords)
        mask = QtGui.QRegion(poly)
        self.setMask(mask)

class ToolsConfig(QtWidgets.QDialog):
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
        self.setFixedSize(widget_width, widget_height)
        self.setGeometry((self.width/2) - (widget_width/2),
                         self.parent.pos().y() - 122,
                         widget_width, widget_height)

        _palette = self.parent.config.parse['colors']
        self.colors = {
            'red': _palette['red'],
            'yellow': _palette['yellow'],
            'green': _palette['green'],
            'blue': _palette['blue'],
            'white': _palette['white'],
            'black': _palette['black']
        }
        self.initUI()
    
    def initUI(self):
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox_left_outer_0 = QHBoxLayout()
        vbox_left_inner = QVBoxLayout()

        qf = QFrame()
        qf.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        lab = QLabel("Foreground color")
        two_1 = QHBoxLayout()
        two_2 = QHBoxLayout()
        two_3 = QHBoxLayout()

        self.pens = {x:QPushButton() for x in self.colors.keys()}

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

        for key in self.pens.keys():
            self.pens[key].setStyleSheet(self.btn_css % self.colors[key])
            self.pens[key].clicked.connect(self.pen_sel)

        two_1.addWidget(self.pens['red'])
        two_1.addWidget(self.pens['blue'])
        two_2.addWidget(self.pens['green'])
        two_2.addWidget(self.pens['yellow'])
        two_3.addWidget(self.pens['black'])
        two_3.addWidget(self.pens['white'])

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

        lab_brush = QLabel("Background color")
        two_1_brush = QHBoxLayout()
        two_2_brush = QHBoxLayout()
        two_3_brush = QHBoxLayout()
 
        self.brushes = {x:QPushButton() for x in self.colors.keys()}

        for cc, key in enumerate(self.brushes.keys()):
            self.brushes[key].setStyleSheet(self.btn_css % self.colors[key])
            self.brushes[key].clicked.connect(self.brush_sel)

        two_1_brush.addWidget(self.brushes['red'])
        two_1_brush.addWidget(self.brushes['blue'])

        two_2_brush.addWidget(self.brushes['green'])
        two_2_brush.addWidget(self.brushes['yellow'])

        two_3_brush.addWidget(self.brushes['black'])
        two_3_brush.addWidget(self.brushes['white'])

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
        right_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
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
        styles = [
                  ["solid", Qt.SolidLine],
                  ["dash", Qt.DashLine],
                  ["dot", Qt.DotLine],
                  ["dashdot", Qt.DashDotLine]
                ]
        for i in range(4):
            if ind == i:
                self.parent.pen_style = styles[i][1]
        
        self.parent.config.changeConfig("canvas", "last_style", styles[ind][0])

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
        balloon_w = 30
        wndRect = self.rect()
        self.wndRect = wndRect
        poly_cords = (
            QPoint(wndRect.x(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),

            QPoint(wndRect.x() + wndRect.width(), wndRect.y()),
            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width(), wndRect.height() - balloon_h),
            QPoint(wndRect.x() + wndRect.width() / 2 - balloon_w / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x() + wndRect.width() / 2, wndRect.height()),
            QPoint(wndRect.x() + wndRect.width() / 2 + balloon_w / 2, wndRect.height() - balloon_h),

            QPoint(wndRect.x(), wndRect.height() - balloon_h)
        )
        poly = QtGui.QPolygon(poly_cords)
        mask = QtGui.QRegion(poly)
        self.setMask(mask)

    def reset_pen_btn_css(self):
        for key in self.pens.keys():
            self.pens[key].setStyleSheet(self.btn_css % self.colors[key])

    def reset_brush_btn_css(self):
        for key in self.brushes.keys():
            self.brushes[key].setStyleSheet(self.btn_css % self.colors[key])

    @QtCore.pyqtSlot()
    def pen_sel(self, key=None):
        def submit(key):
            self.reset_pen_btn_css()
            self.pens[key].setStyleSheet(self.btn_css_active % self.colors[key])
            self.parent.current_pen_color = hex_to_rgb(self.colors[key])
            self.parent.config.changeConfig("canvas", "last_pen_color", self.colors[key])
            self.parent.update_pen_color()
        if key:
            submit(key)
            return
        for key in self.pens.keys():
            if self.sender() is self.pens[key]:
                submit(key)
                return

    def brush_sel(self, key=None):
        def submit(key):
            self.reset_brush_btn_css()
            self.brushes[key].setStyleSheet(self.btn_css_active % self.colors[key])
            self.parent.current_brush_color = hex_to_rgb(self.colors[key])
            self.parent.config.changeConfig("canvas", "last_brush_color", self.colors[key])
            self.parent.update_brush_color()
        if key:
            submit(key)
            return
        for key in self.brushes.keys():
            if self.sender() is self.brushes[key]:
                submit(key)
                return

class Toolkit(BaseLayer):
    def __init__(self, parent, config, fallback):
        super().__init__()
        self.config = config
        self.parent = parent

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        widget_width, widget_height = 400, 240
        self.setFixedSize(widget_width, widget_height)
        self.setGeometry((self.width - widget_width) / 2,
                         self.height - widget_height,
                         widget_width, widget_height)

        self.switch = 0
        self.switches = [['blur', 6], 
                         ['free', 5], ['line', 4],
                         ['rect', 3], ['circle', 2],
                         ['pen', 1], ['sel', 0]]

        self.pen_op = self.config.parse["config"]["canvas"]["pen_opacity"]
        self.brush_op = self.config.parse["config"]["canvas"]["brush_opacity"]

        self.brush_selection_color = QtGui.QColor(103, 150, 188, 40)
        self.pen_selection_color = QtGui.QColor(103, 150, 188, 100)

        _pen = self.config.parse["config"]["canvas"]["last_pen_color"]
        _brush = self.config.parse["config"]["canvas"]["last_brush_color"]

        _def_col = self.parent.config.parse['colors']['red']
        self.current_pen_color = hex_to_rgb(_def_col) if not _pen else hex_to_rgb(_pen)
        self.current_brush_color = hex_to_rgb(_def_col) if not _brush else hex_to_rgb(_brush)

        self.update_pen_color()
        self.update_brush_color()

        self.pen_size = self.config.parse["config"]["canvas"]["last_size"]

        styles = [["solid", Qt.SolidLine],
                  ["dash", Qt.DashLine],
                  ["dot", Qt.DotLine],
                  ["dashdot", Qt.DashDotLine]]

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

        self.tools_config = ToolsConfig(self)
        self.tools_config_outline = ToolsConfigOutline(self)
        if not _brush:
            self.tools_config.brush_sel('red')
        else:
            for key in self.tools_config.colors.keys():
                if _brush == self.tools_config.colors[key]:
                    self.tools_config.brush_sel(key)
        if not _pen:
            self.tools_config.pen_sel('red')
        else:
            for key in self.tools_config.colors.keys():
                if _pen == self.tools_config.colors[key]:
                    self.tools_config.pen_sel(key)
        self.masked = False
        self.initUI()

    def initUI(self):
        grid = QGridLayout(self)

        _tools = ['sel', 'rect', 'line', 'pen',
                  'circle', 'free', 'color', 'blur',
                  'close', 'save']
        if self.config.parse['config']['canvas']['upload_service'] != 'Disabled':
            _tools.append('upload')

        self.tools = {x:QPushButton() for x in _tools}

        self.btn_css = (
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

        self.btn_css_32 = self.btn_css.replace('64px', '32px')

        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(8)
        self.setLayout(grid)

        for key in self.tools.keys():
            self.tools[key].setStyleSheet(self.get_css(key))
            self.tools[key].clicked.connect(self.tool_sel)

        vspace = QSpacerItem(0, 0, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding)
 
        left_grid = QGridLayout()
        left_grid.addWidget(self.tools['rect'], 0, 0)
        left_grid.addWidget(self.tools['circle'], 1, 0)
        left_grid_frame = QFrame()
        left_grid_frame.setStyleSheet('QPushButton { width: 32px }')
        left_grid_frame.setLayout(left_grid)

        right_grid = QGridLayout()
        right_grid.addWidget(self.tools['line'], 0, 0)
        right_grid.addWidget(self.tools['free'], 1, 0)
        right_grid_frame = QFrame()
        right_grid_frame.setStyleSheet('QPushButton { width: 32px }')
        right_grid_frame.setLayout(right_grid)

        grid.addWidget(self.tools['save'], 0, 1)
        if self.config.parse['config']['canvas']['upload_service'] != 'Disabled':
            grid.addWidget(self.tools['upload'], 0, 2)
        grid.addWidget(self.tools['close'], 0, 3)
        grid.addWidget(self.tools['sel'], 1, 2)
        grid.addWidget(self.tools['pen'], 1, 0)
        grid.addWidget(self.tools['color'], 2, 2)
        grid.addWidget(left_grid_frame, 1, 1, 2, 1)
        grid.addWidget(right_grid_frame, 1, 3, 2, 1)
        grid.addWidget(self.tools['blur'], 1, 4)
        grid.addItem(vspace, 4, 0, 1, -1)

    def get_css(self, key, active=False):
        size_32 = ['rect', 'circle', 'line', 'free']

        _css = self.btn_css
        if key in size_32:
            _css = self.btn_css_32

        if not active:
            return _css % (sys.path[0], key,
                           sys.path[0], key+'_hover')
        else:
            return _css % (sys.path[0], key+'_hover',
                           sys.path[0], key+'_hover')

    def closeEvent(self, event):
        self.tools_config_outline.setWindowOpacity(0)
        self.tools_config_outline.close()
        self.tools_config.setWindowOpacity(0)
        self.tools_config.close()
        self.setWindowOpacity(0)
        self.close()

    def close_clicked(self):
        self.close()
        self.parent.close()

    def showEvent(self, event):
        self.show()
        self.setWindowOpacity(1)
        self.redefine_css()
        if not self.masked:
            pix = QtGui.QPixmap(400, 240)
            pix.fill(QtGui.QColor('transparent'))
            self.render(pix, QPoint(), QtGui.QRegion(QtCore.QRect(0, 0, 400, 240)))
            self.setMask(pix.mask())
            self.masked = True

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

    def reset_css(self, check=True):
        if check:
            self.check_color()
        for key in self.tools.keys():
            self.tools[key].setStyleSheet(self.get_css(key))

    def redefine_css(self):
        self.reset_css()
        for item in self.switches:
            if item[1] == self.switch:
                self.tool_sel(item[0])

    @QtCore.pyqtSlot()
    def tool_sel(self, key=False):
        def submit(key):
            self.tools[key].setStyleSheet(self.get_css(key, True))
            for switch in self.switches:
                if key == switch[0]:
                    self.switch = switch[1]

        if key:
            submit(key)
            return

        for key in self.tools.keys():
            if self.sender() == self.tools[key]:
                if key == 'color':
                    self.color_selected()
                    return
                elif key == 'save':
                    self.save_action()
                    return
                elif key == 'upload':
                    self.parent.upload_image()
                    return
                elif key == 'close':
                    self.close_clicked()
                    return
                else:
                    self.reset_css()
                    submit(key)
                    return 

    def color_selected(self):
        self.reset_css(check=False)
        if self.tools_config.isVisible():
            self.tools['color'].setStyleSheet(self.get_css('color'))
            self.tools_config_outline.setWindowOpacity(0)
            self.tools_config.close()
            self.tools_config_outline.close()
            self.redefine_css()
        else:
            self.tools['color'].setStyleSheet(self.get_css('color', True))
            self.tools_config_outline.setWindowOpacity(0)
            self.tools_config_outline.setStyleSheet("background: #131313;")
            self.tools_config_outline.show()
            self.tools_config_outline.setWindowOpacity(0.6)
            self.tools_config.setWindowOpacity(1)
            self.tools_config.show()
            self.tools_config_outline.raise_()
            self.tools_config.raise_()

    def check_color(self):
        if self.tools_config.isVisible():
            self.tools['color'].setStyleSheet(self.get_css('color'))
            self.tools_config_outline.setWindowOpacity(0)
            self.tools_config.close()
            self.tools_config_outline.close()
