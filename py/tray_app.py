from PyQt5.QtGui import QPainter, QImage, QPalette, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from time import sleep
import os
import gc

from screen_window import ScreenWindow
from image_toolkit import ImageToolkit
from main_window import MainWindow

import sys, signal, socket
from PyQt5 import QtCore, QtNetwork

class SignalWakeupHandler(QtNetwork.QAbstractSocket):

    def __init__(self, parent, parent_emit):
        """
        Catch up SIGCONT to invoke capture window instead.
        Without custom handlers SIGCONT is ignored anyway,
        so we may as well take advantage of it.
        https://stackoverflow.com/a/37229299
        """
        super().__init__(QtNetwork.QAbstractSocket.UdpSocket, parent)
        self.parent_emit = parent_emit
        self.old_fd = None
        self.wsock, self.rsock = socket.socketpair(type=socket.SOCK_DGRAM)
        self.setSocketDescriptor(self.rsock.fileno())
        self.wsock.setblocking(False)
        self.old_fd = signal.set_wakeup_fd(self.wsock.fileno())
        self.readyRead.connect(lambda : None)
        # Second handler does the real handling
        self.readyRead.connect(self._readSignal)

    def __del__(self):
        if self.old_fd is not None and signal and signal.set_wakeup_fd:
            signal.set_wakeup_fd(self.old_fd)

    def _readSignal(self):
        data = self.readData(1)
        self.signalReceived.emit(data[0])

    signalReceived = QtCore.pyqtSignal(int)

class Tray(QtWidgets.QWidget):
    trigger = QtCore.pyqtSignal()
    
    def __init__(self, app, app_config):
        super().__init__()
        self.app = app
        self.config = app_config
        self.window = None
        self.main_window = None

        SignalWakeupHandler(self.app, self)
        
        signal.signal(signal.SIGCONT, lambda x,_: self.initCapture())

        self.chz_ico = QtGui.QIcon(os.path.join(
                            sys.path[0], 'img', 'ico_colored.png')
                        )
        _set_ico = self.config.parse['config']['icon']
        self.chz_ico_tray = QtGui.QIcon(os.path.join(
                                sys.path[0], 'img', f'ico_{_set_ico}.png')
                            )
        self.img_toolkit = ImageToolkit(self.app, self.config)

        self.last_out = ''
        self.last_url = ''

        self.setGeometry(0,0,0,0)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint \
                            | QtCore.Qt.FramelessWindowHint \
                            | QtCore.Qt.X11BypassWindowManagerHint)
        self.trigger.connect(self.initCapture)
        self.initTray()
        self.initCapture()
        #self.initScreen()

    def initCapture(self):
        try:
            del self.window
        except AttributeError:
            pass
        self.window = ScreenWindow(self.app, self.config, self.img_toolkit)
        self.window.show()

    def initScreen(self):
        try:
            del self.main_window
        except AttributeError:
            pass
        self.main_window = MainWindow(self, self.app, self.config, self.img_toolkit)
        self.main_window.setWindowIcon(self.chz_ico)
        self.main_window.show()

    def initTray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.chz_ico_tray)

        capture_action = QtWidgets.QAction("Capture", self)
        show_action = QtWidgets.QAction("Show", self)
        quit_action = QtWidgets.QAction("Exit", self)

        capture_action.triggered.connect(self.initCaptureCheck)
        show_action.triggered.connect(self.initMainCheck)
        quit_action.triggered.connect(self.close)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(capture_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        exit(0)

    @QtCore.pyqtSlot()
    def initCaptureCheck(self):
        gc.collect()
        try:
            if self.window and self.window.isVisible():
                print("Dialog already exists")
            else:
                sleep(self.config.parse["config"]["default_delay"])
                self.initCapture()
        except RuntimeError:
            # C++ window destroyed
            sleep(self.config.parse["config"]["default_delay"])
            self.initCapture()

    def initMainCheck(self):
        gc.collect()
        if self.main_window and self.main_window.isVisible():
            print("Dialog already exists")
        else:
            self.initScreen()

