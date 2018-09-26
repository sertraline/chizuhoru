#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from processing import SHOTNAME, SHOTPATH

class BaseLayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        __screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.height, self.width = __screen.height(), __screen.width()
        self.setGeometry(0,0,self.width,self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for i in range(4)]
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

class LoopZoop(BaseLayer):     
    def __init__(self):
        super().__init__()
        self.zoom = 4
        self.initUI()
        self.setGeometry((self.width - 165), 15, 120, 120)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)

    def initUI(self):                
        self.img = QtGui.QPixmap(SHOTPATH[0])
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.img)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.scale(self.zoom, self.zoom)

class Crosshair(LoopZoop):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.zoom = 1
        self.initUI()
        self.setWindowOpacity(0.15)

    def initUI(self):
        self.img = QtGui.QPixmap("{}/src/crosshair.png".format(sys.path[0]))
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addPixmap(self.img)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.scale(self.zoom, self.zoom)

class LePalette(BaseLayer):     
    def __init__(self):
        super().__init__()
        self.setGeometry((self.width / 2 - 120), (self.height - 46), 240, 20)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.pen = "#e81832"
        self.brush = 0
        self.initUI()

    def initUI(self):
        red, blue, green, yellow, black, white = [QtWidgets.QPushButton("", self) for i in range(0, 6)]
        self.fill = QtWidgets.QCheckBox("", self)
        red.setGeometry(0, 0, 20, 20)
        red.setStyleSheet("background-color: #e81832; border: 2px solid black; border-radius: 8px;")
        red.clicked.connect(self.redded)
        blue.setGeometry(20, 0, 20, 20)
        blue.setStyleSheet("background-color: #2459c8; border: 2px solid black; border-radius: 8px;")
        blue.clicked.connect(self.blued)
        green.setGeometry(40, 0, 20, 20)
        green.setStyleSheet("background-color: #23c84f; border: 2px solid black; border-radius: 8px;")
        green.clicked.connect(self.greened)
        yellow.setGeometry(60, 0, 20, 20)
        yellow.setStyleSheet("background-color: #c8ac23; border: 2px solid black; border-radius: 8px;")
        yellow.clicked.connect(self.yellowed)
        black.setGeometry(80, 0, 20, 20)
        black.setStyleSheet("background-color: black; border: 2px solid white; border-radius: 8px;")
        black.clicked.connect(self.blacked)
        white.setGeometry(100, 0, 20, 20)
        white.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 8px;")
        white.clicked.connect(self.whited)
        self.info = QtWidgets.QLabel(self)
        self.info.setText('Fill:')
        self.info.move(150, 1)
        self.info.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 4px;")
        self.fill.setGeometry(190, 0, 20, 20)

    @QtCore.pyqtSlot()
    def redded(self):
        self.pen = "#e81832"
    def blued(self):
        self.pen = "#2459c8"
    def greened(self):
        self.pen = "#23c84f"
    def yellowed(self):
        self.pen = "#c8ac23"
    def blacked(self):
        self.pen = "black"
    def whited(self):
        self.pen = "white"

class Toolkit(BaseLayer):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setGeometry((self.width / 2 - 120), (self.height - 25), 240, 25)
        self.setWindowOpacity(0.85)
        self.switch = 0
        self.thickness = 4
        self.isopened = 0
        self.initUI()

    def update_label(self):
        self.drawThickness.setText("Thickness: {}".format(self.thickness))
        self.drawThickness.update()

    def initUI(self):
        select, blur, circle, rectangle, line = [QtWidgets.QPushButton("", self) for i in range(0, 5)]
        self.drawThickness = QtWidgets.QLabel(self)
        self.drawThickness.setText("Thickness: {}".format(self.thickness))
        self.drawThickness.setFixedWidth(92)
        self.drawThickness.move(150, 4)
        self.drawThickness.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 4px;")

        select.clicked.connect(self.selected)
        select.setGeometry(0, 0, 24, 24)
        select.setIcon(QtGui.QIcon("{}/src/selection.png".format(sys.path[0])))
        select.setIconSize(QtCore.QSize(18, 18))
        select.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 4px; }\
                              QPushButton:pressed { background-color: #acacac; }")
        blur.setIcon(QtGui.QIcon("{}/src/blur.png".format(sys.path[0])))
        blur.setIconSize(QtCore.QSize(18, 18))
        blur.clicked.connect(self.blurred)
        blur.setGeometry(25, 0, 24, 24)
        blur.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 4px; }\
                              QPushButton:pressed { background-color: #acacac; }")
        circle.setIcon(QtGui.QIcon("{}/src/circle.png".format(sys.path[0])))
        circle.setIconSize(QtCore.QSize(18, 18))
        circle.clicked.connect(self.circled)
        circle.setGeometry(50, 0, 24, 24)
        circle.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 4px; }\
                              QPushButton:pressed { background-color: #acacac; }")
        rectangle.setIcon(QtGui.QIcon("{}/src/rectangle.png".format(sys.path[0])))
        rectangle.setIconSize(QtCore.QSize(18, 18))
        rectangle.clicked.connect(self.rectangled)
        rectangle.setGeometry(75, 0, 24, 24)
        rectangle.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 4px; }\
                              QPushButton:pressed { background-color: #acacac; }")
        line.setIcon(QtGui.QIcon("{}/src/line.png".format(sys.path[0])))
        line.setIconSize(QtCore.QSize(18, 18))
        line.clicked.connect(self.lined)
        line.setGeometry(100, 0, 24, 24)
        line.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 4px; }\
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
