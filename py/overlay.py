#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt

class BaseLayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        __screen = QtWidgets.QDesktopWidget().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)
        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), __screen_geo.width(), __screen_geo.left(), __screen_geo.top()
        self.setGeometry(0,0,self.width,self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for i in range(4)]
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

class LePalette(BaseLayer):     
    def __init__(self):
        super().__init__()
        self.move(self.left, self.top)
        self.setGeometry((self.left + (self.width / 2 - 120)), (self.top + (self.height - 46)), 320, 20)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.pen = "#e81832"
        self.brush = 0
        self.initUI()

    def initUI(self):
        red, blue, green, yellow, black, white = [QtWidgets.QPushButton("", self) for i in range(0, 6)]
        self.fill = 0
        red.setGeometry(0, 0, 34, 20)
        red.setStyleSheet("background-color: #f22c40; border: 1px solid black; border-right: 0;")
        red.clicked.connect(self.redded)
        blue.setGeometry(30, 0, 34, 20)
        blue.setStyleSheet("background-color: #407ee7; border: 1px solid black; border-left: 0; border-right: 0;")
        blue.clicked.connect(self.blued)
        green.setGeometry(60, 0, 34, 20)
        green.setStyleSheet("background-color: #5ab738; border: 1px solid black; border-left: 0;  border-right: 0;")
        green.clicked.connect(self.greened)
        yellow.setGeometry(90, 0, 34, 20)
        yellow.setStyleSheet("background-color: #d5911a; border: 1px solid black; border-left: 0;  border-right: 0;")
        yellow.clicked.connect(self.yellowed)
        black.setGeometry(120, 0, 34, 20)
        black.setStyleSheet("background-color: black; border: 1px solid black; border-left: 0;  border-right: 0;")
        black.clicked.connect(self.blacked)
        white.setGeometry(150, 0, 34, 20)
        white.setStyleSheet("background-color: white; border: 1px solid black; border-left: 0; ")
        white.clicked.connect(self.whited)
        self.info = QtWidgets.QPushButton(self)
        self.info.setText('  FILL  ')
        self.info.move(200, 2)
        self.info.setStyleSheet("background-color: white; border: 1px solid black; font-size: 8pt;")
        self.info.clicked.connect(self.filled)

    @QtCore.pyqtSlot()
    def redded(self):
        self.pen = "#f22c40"
    def blued(self):
        self.pen = "#407ee7"
    def greened(self):
        self.pen = "#5ab738"
    def yellowed(self):
        self.pen = "#d5911a"
    def blacked(self):
        self.pen = "black"
    def whited(self):
        self.pen = "white"

    def filled(self):
        self.fill = 0 if self.fill == 1 else 1
        if self.fill == 0:
            self.info.setStyleSheet("background-color: white; border: 1px solid black; font-size: 8pt;")
        else:
            self.info.setStyleSheet("background-color: #7f7f7f; border: 1px solid black; font-size: 8pt;")

class Toolkit(BaseLayer):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setGeometry((self.left + (self.width / 2 - 120)), (self.top + (self.height - 25)), 240, 20)
        self.setWindowOpacity(0.85)
        self.switch = 0
        self.thickness = 4
        self.isopened = 0
        self.initUI()

    def initUI(self):
        select, rectangle, line, blur, circle = [QtWidgets.QPushButton("", self) for i in range(0, 5)]

        select.clicked.connect(self.selected)
        select.setGeometry(0, 0, 24, 20)
        select.setIcon(QtGui.QIcon("{}/src/selection.png".format(sys.path[0])))
        select.setIconSize(QtCore.QSize(16, 16))
        select.setStyleSheet("QPushButton { background-color: white; border: 0px solid black; border: 1px solid black;}\
                              QPushButton:pressed { background-color: #acacac; }")
        rectangle.setIcon(QtGui.QIcon("{}/src/rectangle.png".format(sys.path[0])))
        rectangle.setIconSize(QtCore.QSize(16, 16))
        rectangle.clicked.connect(self.rectangled)
        rectangle.setGeometry(24, 0, 24, 20)
        rectangle.setStyleSheet("QPushButton { background-color: white; border: 0px solid black; border: 1px solid black; }\
                              QPushButton:pressed { background-color: #acacac; }")
        line.setIcon(QtGui.QIcon("{}/src/line.png".format(sys.path[0])))
        line.setIconSize(QtCore.QSize(16, 16))
        line.clicked.connect(self.lined)
        line.setGeometry(48, 0, 24, 20)
        line.setStyleSheet("QPushButton { background-color: white; border: 0px solid black; border: 1px solid black;}\
                              QPushButton:pressed { background-color: #acacac; }")
        blur.setIcon(QtGui.QIcon("{}/src/blur.png".format(sys.path[0])))
        blur.setIconSize(QtCore.QSize(16, 16))
        blur.clicked.connect(self.blurred)
        blur.setGeometry(72, 0, 24, 20)
        blur.setStyleSheet("QPushButton { background-color: white; border: 0px solid black; border: 1px solid black;}\
                              QPushButton:pressed { background-color: #acacac; }")
        circle.setIcon(QtGui.QIcon("{}/src/circle.png".format(sys.path[0])))
        circle.setIconSize(QtCore.QSize(16, 16))
        circle.clicked.connect(self.circled)
        circle.setGeometry(96, 0, 24, 20)
        circle.setStyleSheet("QPushButton { background-color: white; border: 0px solid black; border: 1px solid black;}\
                              QPushButton:pressed { background-color: #acacac; }")

    @QtCore.pyqtSlot()
    def lined(self):
        self.switch = 4
    def rectangled(self):
        self.switch = 3
    def circled(self):
        self.switch = 2
    def blurred(self):
        self.switch = 1
    def selected(self):
        self.switch = 0
