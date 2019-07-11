#!/usr/bin/python3
import sys
from time import sleep
from argparse import ArgumentParser
from os import remove, path, getpid, environ, unlink, kill
from PyQt5.QtGui import QPainter, QImage, QPalette, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PIL.ImageQt import ImageQt
import json
import overlay
import processing

class ScreenWindow(overlay.BaseLayer):
    __slots__ = ()

    def __init__(self):
        super().__init__()
        # move instance to the current monitor
        self.move(self.left, self.top)
        processing.scrot(self.screen)

        #update screenshot name and path
        processing.SHOTNAME = fr"{processing.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        processing.SHOTPATH[0] = f"/tmp/{processing.SHOTNAME}"
        processing.SHOTPATH[1] = f"{args['directory']}/{processing.SHOTNAME}" if args[
            "directory"] != None else None
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.save_dialog = SaveDialog()
        self.toolkit = overlay.Toolkit()
        self.color_palette = overlay.LePalette()

        self.showFullScreen()
        self.background()

        self.actions = processing.Stack()
        self.cords = None  
        # ^ active window coordinates

    def background(self):
        # Renders screenshot as background
        img = ImageQt(processing.TEMP)
        oImage = QImage(img)
        sImage = oImage.scaled(QSize(self.width,self.height))
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(103, 150, 188, 60))
        qp.setBrush(br)
        if not self.cords:
            rect = QtCore.QRect(self.begin, self.end)
            self.rectx, self.recty, self.rectw, self.recth = list(rect.getRect())
            self.detailedcoord = list(rect.getCoords())
            if self.toolkit.switch == 2:
                qp.drawEllipse(rect)
            elif self.toolkit.switch == 4:
                qp.drawLine(self.begin.x(), self.begin.y(), self.end.x(), self.end.y())
            elif self.toolkit.switch == 5:
                br = QtGui.QPen(QtGui.QColor(103, 150, 188, 60), 4)
                qp.setPen(br)
                qp.drawPoint(self.end.x(), self.end.y())
            else:
                qp.drawRect(rect)
        else:
            qp.drawRect(self.cords)
            self.cords = None
    
    def redrawImage(self):
        # updates background
        self.background()
        self.update()

    def closeScreen(self):
        if path.isfile(processing.SHOTPATH[0]):
            remove(processing.SHOTPATH[0])
        self.close()
        self.toolkit.close()
        self.color_palette.close()
  
    def hideScreen(self):
        self.hide()
        self.toolkit.hide()
        self.color_palette.hide()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()
        self.color_palette.brush = 1 if self.color_palette.fill.isChecked() else 0
        # ensure that we will have exactly a rectangle and not an accidental click
        if self.toolkit.switch != 0:
            if self.toolkit.switch == 1 and abs(self.rectw) >= 2:
                rectangle_pos = [self.rectw, self.recth, self.rectx, self.recty]
                processing.blur(rectangle_pos, self.actions)
            elif self.begin != self.end:
                if self.toolkit.switch == 2:
                    processing.circle(
                        self.begin, self.end, self.toolkit.thickness, self.actions, self.color_palette.pen, self.color_palette.brush)
                elif self.toolkit.switch == 3:
                    processing.drawrectangle(
                        self.begin, self.end, self.toolkit.thickness, self.actions, self.color_palette.pen, self.color_palette.brush)
                elif self.toolkit.switch == 4:
                    processing.drawline(
                        self.begin, self.end, self.toolkit.thickness, self.actions, self.color_palette.pen)
            self.redrawImage()     
            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()

    def wheelEvent(self, event):
        if event.angleDelta().y() + abs(event.angleDelta().y()) == 0:
            if self.toolkit.thickness != 1:
                self.toolkit.thickness -= 1
        else:
            if self.toolkit.thickness < 20:
                self.toolkit.thickness += 1

    def keyPressEvent(self, qKeyEvent):
        if (qKeyEvent.nativeModifiers() == 4 or qKeyEvent.nativeModifiers() == 8196
        ) and (qKeyEvent.nativeScanCode() == 52):
        # is responsible for Ctrl-Z both in English and Cyrillic moonspeak
            shouldi = self.actions.extract()
            if not shouldi:
                self.redrawImage()
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            if self.save_dialog.checkbox_tab2.isChecked():
                shadowargs = [config.userSpace, config.userShadowSize, config.userIterations, config.roundCorners]
            else:
                shadowargs = []
            if abs(self.rectw) <= 1 and abs(self.recth) <= 1:
                rectangle_pos = [self.width, self.height, 0, 0]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            else:
                rectangle_pos = [self.rectw, self.recth, self.rectx, self.recty]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            self.closeScreen()
        if qKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.closeScreen()
        if qKeyEvent.nativeScanCode() == 28: #"T" key
            if self.toolkit.isopened == 0:
                self.toolkit.show()
                self.color_palette.show()
                self.toolkit.isopened = 1
            else:
                self.toolkit.hide()
                self.color_palette.hide()
                self.toolkit.isopened = 0
        if qKeyEvent.nativeScanCode() == 39: #"S" key
            self.save_dialog.args = [self.rectw, self.recth, self.rectx, self.recty, processing.SHOTPATH]
            self.hideScreen()
            self.save_dialog.show()
        if qKeyEvent.nativeScanCode() == 30: #"U" key
            self.save_dialog.args = [self.rectw, self.recth, self.rectx, self.recty, processing.SHOTPATH]
            self.save_dialog.pushImgurUpload()
            self.close()
        if qKeyEvent.nativeScanCode() == 38: #"A" key
            self.hideScreen()
            self.rectw, self.recth, self.rectx, self.recty = processing.grep_window()
            point_zero = QtCore.QPoint(self.rectx, self.recty)
            point_one = QtCore.QPoint((self.rectx+self.rectw), (self.recty+self.recth))
            self.cords = QtCore.QRect(point_zero, point_one)
            self.show()
        self.update()

class InitListener(QtCore.QThread):
    __slots__ = ("parent")

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def run(self):
        """Checks for attempts to run second instance"""
        while True:
            if path.isfile("/tmp/chizuhoru.pid.exit"):
                remove("/tmp/chizuhoru.pid.exit")
                self.parent.trigger.emit()
            # python will take all of your CPU if you remove sleep().
            sleep(1)

class Tray(QtWidgets.QWidget):
    __slots__ = ()
    trigger = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setGeometry(0,0,0,0)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        self.trigger.connect(self.initScreen)
        self.initTray()
        self.initScreen()

    def initScreen(self):
        # remove the reference to the last ScreenWindow
        # to clear some memory
        try:
            del self.window
        except AttributeError:
            pass
        self.window = ScreenWindow()
        self.window.show()

    def initTray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(f"{sys.path[0]}/src/ico.png"))

        self.listener = InitListener(parent=self)
        self.listener.start()

        show_action = QtWidgets.QAction("Show", self)
        config_action = QtWidgets.QAction("Configure", self)
        quit_action = QtWidgets.QAction("Exit", self)
        config_action.triggered.connect(self.initConfig)
        show_action.triggered.connect(self.initScreenCheck)
        quit_action.triggered.connect(self.close)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(config_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        if path.isfile(processing.SHOTPATH[0]):
            remove(processing.SHOTPATH[0])
        QtWidgets.qApp.quit()

    @QtCore.pyqtSlot()
    def initScreenCheck(self):
        if self.window.save_dialog.isVisible():
            print("Dialog already exists")
        else:
            self.initScreen()


    def initConfig(self):
        self.config = EditConfig()

class SaveDialog(QtWidgets.QWidget):
    __slots__ = ()

    def __init__(self):
        super().__init__()
        __screen = QtWidgets.QDesktopWidget().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)
        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), __screen_geo.width(), __screen_geo.left(), __screen_geo.top()
        self.setGeometry((self.left + (self.width / 2 - 200)), (self.top + (self.height / 2)), 400, 350)
        self.setFixedSize(400, 350)
        self.setWindowTitle("Save / Upload")
        
        # args: retrieves self.rectw, self.recth, self.rectx, self.recty, processing.SHOTPATH
        self.args = []
        self.fname = processing.SHOTPATH[1] if (processing.SHOTPATH[1] != None) else (
            f"/home/{environ['USER']}/{processing.SHOTNAME}")
        self.upload_preset = "custom"
        self.initLayout()
    
    def initLayout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        
        self.tab1, self.tab2, self.tab3, self.tab4 = [
            QtWidgets.QWidget() for i in range(4)
        ]
        
        self.tabs.addTab(self.tab1,"Main")
        self.tabs.addTab(self.tab2,"Upload to host")
        self.tabs.addTab(self.tab3,"Encode")
        self.tabs.addTab(self.tab4,"Decode")
        
        self.initTabOne()
        self.initTabTwo()
        self.initTabThree()
        self.initTabFour()
        
        self.layout.addWidget(self.tabs)
        
        self.push_settings = QtWidgets.QPushButton("Config")
        self.push_settings.clicked.connect(self.initConfig)
        
        self.layout.addWidget(self.push_settings, QtCore.Qt.AlignRight)
        
        self.setLayout(self.layout)

    def initTabOne(self):
        # Main tab
        self.tab1.main_0_layout = QtWidgets.QGridLayout()
        # wrapper wraps main_0_layout
        self.tab1.main_0_wrapper = QtWidgets.QGroupBox()
        self.tab1.main_0_wrapper.setFixedSize(355, 110)
        self.tab1.main_0_wrapper.setTitle("Save to")
        self.tab1.main_0_wrapper.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        
        self.tab1.main_1_layout = QtWidgets.QHBoxLayout()
        # vertical wrapper wraps wrapper and main_1_layout
        self.tab1.vertical_wrapper = QtWidgets.QVBoxLayout()
        
        # textbox: picture filename
        self.textbox = QtWidgets.QLineEdit(f"{processing.SHOTNAME}")
        self.textbox.textChanged.connect(self.changeTextboxFilename)
        
        # file picker
        self.save = QtWidgets.QPushButton("Browse")
        self.save.clicked.connect(self.askFilename)
        
        self.checktext0 = QtWidgets.QLabel("Copy to clipboard:")
        self.checkbox0 = QtWidgets.QCheckBox()
        self.checkbox0.setChecked(True)
        
        self.checktext1 = QtWidgets.QLabel("Draw shadows:")
        self.checkbox1 = QtWidgets.QCheckBox()
        self.checkbox1.setChecked(config.shadowDraw)
        
        self.tab1.main_0_layout.addWidget(self.textbox, 1, 0, 1, 1)
        self.tab1.main_0_layout.addWidget(self.save, 1, 1, 1, 1)
        self.tab1.main_0_layout.addWidget(self.checktext0, 2, 0, 1, 1)
        self.tab1.main_0_layout.addWidget(self.checkbox0, 2, 1, 1, 1)
        self.tab1.main_0_layout.addWidget(self.checktext1, 3, 0, 1, 1)
        self.tab1.main_0_layout.addWidget(self.checkbox1, 3, 1, 1, 1)
        
        self.donebutton = QtWidgets.QPushButton("Save and quit")
        self.donebutton.clicked.connect(self.jobIsDone)
        self.tab1.main_1_layout.addStretch(1)

        self.tab1.main_1_layout.addWidget(self.donebutton)
        self.tab1.main_0_wrapper.setLayout(self.tab1.main_0_layout)
        self.tab1.vertical_wrapper.addWidget(self.tab1.main_0_wrapper)
        self.tab1.vertical_wrapper.addLayout(self.tab1.main_1_layout)
        
        self.tab1.setLayout(self.tab1.vertical_wrapper)
    
    def initTabTwo(self):
        # Upload to host tab
        #
        # vertical wrapper wraps shadowHLayout, upload_wrapper, upload_imgur_wrapper
        # shadowHLayout -> draw shadows
        # upload wrapper -> custom uploads
        # upload_imgur_wrapper -> upload to imgur
        self.tab2.vertical_wrapper = QtWidgets.QVBoxLayout()
        # upload_wrapper is responsible for custom uploads
        self.tab2.upload_wrapper = QtWidgets.QGroupBox()
        self.tab2.upload_wrapper.setFixedSize(355, 110)
        self.tab2.upload_wrapper.setTitle("Custom")
        self.tab2.upload_wrapper.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        
        # upload wrapper wraps uploads_hlayouts_wrapper
        self.tab2.upload_hlayouts_wrapper = QtWidgets.QVBoxLayout()
        # upload_hlayouts_wrapper wraps upload_presets_layout, upload_0_hlayout, upload_1_hlayout
        self.tab2.upload_presets_layout = QtWidgets.QHBoxLayout()
        self.tab2.upload_0_hlayout = QtWidgets.QHBoxLayout()
        self.tab2.upload_1_hlayout = QtWidgets.QHBoxLayout()
        
        #CUSTOM
        self.presets_label = QtWidgets.QLabel("Presets:")
        self.presets = QtWidgets.QComboBox()
        self.presets.addItems(["custom", "catbox.moe", "uguu.se"])
        self.presets.currentIndexChanged.connect(self.setPresets)
        
        self.tab2.upload_presets_layout.addWidget(self.presets_label)
        self.tab2.upload_presets_layout.addWidget(self.presets)
        
        self.filename_title = QtWidgets.QLabel("Filename:")
        self.push_filename = QtWidgets.QLineEdit(self)
        self.push_filename.setText(f"{processing.SHOTNAME}")
        self.push_filename.textChanged.connect(self.changeUploadFilename)
        
        self.push_image = QtWidgets.QPushButton("Upload")
        self.push_image.clicked.connect(self.pushUpload)
        
        self.push_link = QtWidgets.QLineEdit("Result link")
        self.push_link.setDisabled(True)
        
        for i in [self.filename_title, self.push_filename, self.push_image]:
            self.tab2.upload_0_hlayout.addWidget(i)
        self.tab2.upload_1_hlayout.addWidget(self.push_link)
        
        self.tab2.upload_hlayouts_wrapper.addLayout(self.tab2.upload_presets_layout)
        self.tab2.upload_hlayouts_wrapper.addLayout(self.tab2.upload_0_hlayout)
        self.tab2.upload_hlayouts_wrapper.addLayout(self.tab2.upload_1_hlayout)
        
        self.tab2.upload_wrapper.setLayout(self.tab2.upload_hlayouts_wrapper)
        
        #IMGUR
        # upload_imgur_wrapper wraps upload_imgur_hlayouts_wrapper
        self.tab2.upload_imgur_wrapper = QtWidgets.QGroupBox()
        self.tab2.upload_imgur_wrapper.setFixedSize(355, 80)
        self.tab2.upload_imgur_wrapper.setTitle("Imgur")
        self.tab2.upload_imgur_wrapper.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        
        # upload_imgur_hlayouts_wrapper wraps upload_imgur_0_hlayout, upload_imgur_1_hlayout
        self.tab2.upload_imgur_hlayouts_wrapper = QtWidgets.QVBoxLayout()
        self.tab2.upload_imgur_0_hlayout = QtWidgets.QHBoxLayout()
        self.tab2.upload_imgur_1_hlayout = QtWidgets.QHBoxLayout()
        
        self.push_imgur_image = QtWidgets.QPushButton("Upload")
        self.push_imgur_image.clicked.connect(self.pushImgurUpload)

        self.push_imgur_link = QtWidgets.QLineEdit("Result link")
        self.push_imgur_link.setDisabled(True)
        
        self.tab2.upload_imgur_0_hlayout.addWidget(self.push_imgur_image)
        self.tab2.upload_imgur_1_hlayout.addWidget(self.push_imgur_link)

        self.tab2.upload_imgur_hlayouts_wrapper.addLayout(self.tab2.upload_imgur_0_hlayout)
        self.tab2.upload_imgur_hlayouts_wrapper.addLayout(self.tab2.upload_imgur_1_hlayout)

        self.tab2.upload_imgur_wrapper.setLayout(self.tab2.upload_imgur_hlayouts_wrapper)
        # END OF THE IMGUR SECTION

        self.checkbox_tab2 = QtWidgets.QCheckBox()
        self.checkbox_tab2.setChecked(config.shadowDraw)
        self.checktext_tab2 = QtWidgets.QLabel("Draw shadows:")
        
        # Set layouts for the whole tab:
        self.tab2.shadowHLayout = QtWidgets.QHBoxLayout()
        self.tab2.shadowHLayout.addWidget(self.checktext_tab2)
        self.tab2.shadowHLayout.addWidget(self.checkbox_tab2)
        self.tab2.shadowHLayout.addStretch(1)
        
        self.tab2.vertical_wrapper.addLayout(self.tab2.shadowHLayout)
        self.tab2.vertical_wrapper.addWidget(self.tab2.upload_wrapper)
        self.tab2.vertical_wrapper.addWidget(self.tab2.upload_imgur_wrapper)
        
        self.tab2.setLayout(self.tab2.vertical_wrapper)

    def initTabThree(self):
        # Encode picture
        # t3_image -> Image or image filepath
        self.t3_image = None
        self.t3_message = ""
        # t3_fname -> path of result image
        self.t3_fname = processing.SHOTNAME

        # vertical_wrapper wraps main_0_wrapper, main_1_layout
        self.tab3.vertical_wrapper = QtWidgets.QVBoxLayout()
        # main_0_wrapper wraps main_0_layout
        self.tab3.main_0_wrapper = QtWidgets.QGroupBox()
        # main_0_layout is responsible for "Encoding" section
        self.tab3.main_0_layout = QtWidgets.QGridLayout()
        self.tab3.main_0_wrapper.setFixedSize(355, 140)
        self.tab3.main_0_wrapper.setTitle("Hide text in the image")
        self.tab3.main_0_wrapper.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        
        # main_1_layout wraps main_1_box
        self.tab3.main_1_layout = QtWidgets.QGroupBox()
        # main_1_box is responsible for "Save to" section
        self.tab3.main_1_box = QtWidgets.QGridLayout()
        self.tab3.main_1_layout.setTitle("Save to")
        self.tab3.main_1_layout.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")

        self.textbox_label = QtWidgets.QLabel("Message")

        self.chooser_label = QtWidgets.QLabel("Image")
        # chooser_options: use current image or choose custom
        self.chooser_options = QtWidgets.QComboBox()
        self.chooser_options.addItems(["current", "custom"])
        self.chooser_options.currentIndexChanged.connect(self.setChooser)

        # t3_textbox: path of the custom image
        self.t3_textbox = QtWidgets.QLineEdit(self.t3_image)
        self.t3_textbox.textChanged.connect(self.changeFilePath)
        
        # file picker -> openFile
        self.t3_save = QtWidgets.QPushButton("Browse")
        self.t3_save.clicked.connect(lambda t3: self.askForFile(tab=3))

        # encoding message box
        self.textbox_q = QtWidgets.QPlainTextEdit()
        self.textbox_q.textChanged.connect(self.changeMessage)

        self.t3_textbox.setDisabled(True)
        self.t3_save.setDisabled(True)

        self.tab3.main_0_layout.addWidget(self.chooser_label, 1, 0, 1, 1)
        self.tab3.main_0_layout.addWidget(self.chooser_options, 1, 1, 1, 1)
        self.tab3.main_0_layout.addWidget(self.t3_textbox, 2, 0, 1, 1)
        self.tab3.main_0_layout.addWidget(self.t3_save, 2, 1, 1, 1)
        self.tab3.main_0_layout.addWidget(self.textbox_label, 3, 0, 1, 1)
        self.tab3.main_0_layout.addWidget(self.textbox_q, 4, 0, 1, 1)

        # prints useful info or errors. Empty as default
        self.err_label = QtWidgets.QLabel("")

        # where to save image: file path textbox
        self.saveto = QtWidgets.QLineEdit(self.t3_fname)
        self.saveto.textChanged.connect(self.changeTextboxFilename)
        
        # file picker -> saveFile
        self.findpath = QtWidgets.QPushButton("Browse")
        self.findpath.clicked.connect(self.askFilename)

        self.encryptbutton = QtWidgets.QPushButton("Encode")
        self.encryptbutton.clicked.connect(self.encode)

        self.tab3.main_1_box.addWidget(self.saveto, 1, 0, 1, 1)
        self.tab3.main_1_box.addWidget(self.findpath, 1, 1, 1, 1)
        self.tab3.main_1_box.addWidget(self.err_label, 3, 0, 1, 1)
        self.tab3.main_1_box.addWidget(self.encryptbutton, 3, 1, 1, 1)

        self.tab3.main_0_wrapper.setLayout(self.tab3.main_0_layout)
        self.tab3.main_1_layout.setLayout(self.tab3.main_1_box)

        self.tab3.vertical_wrapper.addWidget(self.tab3.main_0_wrapper)
        self.tab3.vertical_wrapper.addWidget(self.tab3.main_1_layout)

        self.tab3.setLayout(self.tab3.vertical_wrapper)

    def initTabFour(self):
        # Decode picture
        self.t4_message = ""
        # t4_image: image to decode
        self.t4_image = None

        # vertical_wrapper wraps main_0_wrapper
        self.tab4.vertical_wrapper = QtWidgets.QVBoxLayout()

        # main_0_wrapper wraps main_0_layout
        self.tab4.main_0_wrapper = QtWidgets.QGroupBox()
        self.tab4.main_0_wrapper.setFixedSize(355, 180)
        self.tab4.main_0_wrapper.setTitle("Decode")
        self.tab4.main_0_wrapper.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        
        self.tab4.main_0_layout = QtWidgets.QGridLayout()

        self.t4_textbox_label = QtWidgets.QLabel("Message")

        # t4_textbox: open image to decode textbox
        self.t4_textbox = QtWidgets.QLineEdit()
        self.t4_textbox.textChanged.connect(self.getFilePath)
       
        # file picker -> openFile
        self.t4_open = QtWidgets.QPushButton("Browse")
        self.t4_open.clicked.connect(lambda t4: self.askForFile(tab=4))

        # decoded message
        self.t4_textbox_q = QtWidgets.QPlainTextEdit()
        self.t4_textbox_q.textChanged.connect(self.changeMessage)

        self.decodebutton = QtWidgets.QPushButton("Decode")
        self.decodebutton.clicked.connect(self.decode)

        # prints useful info or errors. Empty as default
        self.t4_err_label = QtWidgets.QLabel("")

        self.tab4.main_0_layout.addWidget(self.t4_textbox, 1, 0, 1, 1)
        self.tab4.main_0_layout.addWidget(self.t4_open, 1, 1, 1, 1)
        self.tab4.main_0_layout.addWidget(self.t4_textbox_label, 2, 0, 1, 1)
        self.tab4.main_0_layout.addWidget(self.t4_textbox_q, 3, 0, 1, 1)
        self.tab4.main_0_layout.addWidget(self.decodebutton)
        self.tab4.main_0_layout.addWidget(self.t4_err_label, 4, 0, 1, 1)

        self.tab4.main_0_wrapper.setLayout(self.tab4.main_0_layout)

        self.tab4.vertical_wrapper.addWidget(self.tab4.main_0_wrapper)

        self.tab4.setLayout(self.tab4.vertical_wrapper)

    def initConfig(self):
        self.config = EditConfig()

    def closeEvent(self, event):
        self.close()
        if path.isfile(processing.SHOTPATH[0]):
            remove(processing.SHOTPATH[0])

    @QtCore.pyqtSlot()
    def askFilename(self):
        # Calls qt filepicker to SAVE and sets textbox to new path value.
        self.fname = self.fname if isinstance(self.fname, str) else self.fname[0]
        self.new_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', self.fname, 'png (*.png *.)')
        self.textbox.setStyleSheet("")
        self.fname = self.new_path[0] if self.new_path[0] else self.fname
        path = self.fname if self.fname.lower().endswith('.png') else self.fname+'.png'
        self.textbox.setText(path)
        self.saveto.setText(path)

    def retrieveFilename(self, name):
        filename = name if isinstance(name, str) else name[0]
        filename = processing.SHOTNAME if not filename else filename
        filename = filename if '.png' in filename.lower() else filename+'.png'
        if not '/' in filename:
            if processing.SHOTPATH[1]:
                filename = processing.SHOTPATH[1].replace(processing.SHOTNAME, filename)
            else:
                filename = f"/home/{environ['USER']}/"+filename
        if '~/' in filename:
            filename = filename.replace('~/', f"/home/{environ['USER']}/")
        processing.SHOTPATH[1] = filename
        return filename

    def jobIsDone(self):
        # Saves image and exits.
        # clip -> copy to clipboard
        clip = int(self.checkbox0.isChecked())
        # draw shadows
        if self.checkbox1.isChecked():
            shadowargs = [
                config.userSpace, config.userShadowSize, config.userIterations, config.roundCorners]
        else:
            shadowargs = []
        filename = self.retrieveFilename(self.fname)
        try:
            if abs(self.args[0]) <= 1 and abs(self.args[1]) <= 1:
                rectangle_pos = [self.width, self.height, 0, 0]
                processing.convert(rectangle_pos, clip, shadowargs=shadowargs)
            else:
                rectangle_pos = [self.args[0], self.args[1], self.args[2], self.args[3]]
                processing.convert(rectangle_pos, clip, shadowargs=shadowargs)
            self.close()
        except ValueError as e:
            pass
        except PermissionError:
            self.textbox.setText("Permission denied")
            self.textbox.setStyleSheet("border: 2px solid red; border-radius: 3px;")

    def changeTextboxFilename(self):
        # textbox from Main tab. Retrieves new filepath to save
        self.fname = self.textbox.text()
        self.t3_fname = self.saveto.text()

    def changeUploadFilename(self):
        # push_filename from upload section. Retrieves new name
        processing.SHOTNAME = self.push_filename.text()

    def setPresets(self):
        # presets from upload section. Retrieves upload preset
        self.upload_preset = self.presets.currentText()

    def setChooser(self):
        # sets tab3 fields to disabled if user is using current screenshot
        if self.chooser_options.currentText() == "current":
            self.t3_save.setDisabled(True)
            self.t3_textbox.setDisabled(True)
            self.t3_image = None
        else:
            self.t3_save.setDisabled(False)
            self.t3_textbox.setDisabled(False)

    def changeFilePath(self):
        # textbox from Encode tab. Sets to new path from user input
        self.t3_image = self.t3_textbox.text()

    def getFilePath(self):
        # textbox from Decode tab. Sets to new path from user input
        self.t4_image = self.t4_textbox.text()

    def askForFile(self, tab):
        # calls qt filepicker to OPEN and sets textbox to new path value.
        new_image = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose file', '', 'png (*.png *.)')
        image_path = new_image[0] if new_image[0] else None
        if image_path != None:
            if image_path.endswith('.png'):
                if tab == 3:
                    self.t3_textbox.setText(self.image_path)
                elif tab == 4:
                    self.t4_textbox.setText(self.image_path)

    def changeMessage(self):
        # textbox_q from Encode tab. Retrieves message to encode
        self.t3_message = self.textbox_q.toPlainText()
        self.textbox_q.setStyleSheet("")

    def encode(self):
        # savepath -> where to save
        savepath = self.retrieveFilename(self.t3_fname)
        try:
            # t3_image -> what to encode
            image = processing.Image.open(self.t3_image
            ) if self.t3_image != None else processing.TEMP
            res = processing.encode(self.t3_message, image, savepath)
            self.err_label.setText(res)
            self.saveto.setStyleSheet("border: 2px solid green; border-radius: 3px;")
        except PermissionError as e:
            self.err_label.setText("Permission denied")
            self.saveto.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        except ValueError as e:
            self.err_label.setText("Your message is empty")
            self.textbox_q.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        except FileNotFoundError:
            self.err_label.setText("File not found")
            self.saveto.setStyleSheet("border: 2px solid red; border-radius: 3px;")

    def decode(self):
        # openpath -> what to decode
        openpath = self.t4_image
        try:
            self.t4_textbox.setStyleSheet("")
            image = processing.Image.open(openpath) if openpath and '/' in openpath else None
            if image:
                result = processing.decode(image)
                self.t4_err_label.setText("")
                self.t4_textbox_q.setPlainText(result)
                self.t4_textbox_q.setStyleSheet("border: 2px solid green; border-radius: 3px;")
            else:
                raise ValueError
        except PermissionError:
            self.t4_err_label.setText("Permission denied")
            self.t4_textbox.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        except UnicodeDecodeError as e:
            self.t4_err_label.setText(f"Image is not encoded or is invalid.")
            self.t4_textbox_q.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        except (ValueError, AttributeError, IsADirectoryError, FileNotFoundError):
            self.t4_err_label.setText("Path or image is invalid")
            self.t4_textbox.setStyleSheet("border: 2px solid red; border-radius: 3px;")

    def pushUpload(self):
        if self.checkbox_tab2.isChecked():
            shadowargs = [config.userSpace, config.userShadowSize, config.userIterations, config.roundCorners]
        else:
            shadowargs = []
        try:
            if abs(self.args[0]) <= 1 and abs(self.args[1]) <= 1:
                rectangle_pos = [self.width, self.height, 0, 0]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            else:
                rectangle_pos = [self.args[0], self.args[1], self.args[2], self.args[3]]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            if self.upload_preset == "custom":
                customArgs = [config.userCustomAccessToken, config.userCustomUsername, 
                config.userCustomPassword, config.userCustomName, config.userCustomLink]
                result = processing.custom_upload(args=customArgs)
            else:
                result = processing.custom_upload(preset=self.upload_preset)
            self.push_link.setDisabled(False)
            self.push_link.setText(result)
            self.push_link.setStyleSheet("border: 2px solid green; border-radius: 3px;")
        except processing.requests.exceptions.ConnectionError as e:
            self.push_link.setText(f"Connection error: {e}")
            self.push_link.setStyleSheet("border: 2px solid red; border-radius: 3px;")
        except processing.NoLinkException as e:
            self.push_link.setDisabled(False)
            self.push_link.setText("Error: link is empty or invalid")
            self.push_link.setStyleSheet("border: 2px solid red; border-radius: 3px;")          

    def pushImgurUpload(self):
        if self.checkbox_tab2.isChecked():
            shadowargs = [config.userSpace, config.userShadowSize, config.userIterations, config.roundCorners]
        else:
            shadowargs = []
        customArgs = [config.userImgurID, config.userImgurLink, config.imgurClipboard]
        try:
            if abs(self.args[0]) <= 1 and abs(self.args[1]) <= 1:
                rectangle_pos = [self.width, self.height, 0, 0]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            else:
                rectangle_pos = [self.args[0], self.args[1], self.args[2], self.args[3]]
                processing.convert(rectangle_pos, shadowargs=shadowargs)
            result = processing.imgur_upload(customArgs)
            self.push_imgur_link.setDisabled(False)
            self.push_imgur_link.setText(result)
            if config.imgurClipboard:
                self.push_imgur_image.setText("Copied to clipboard")
            self.push_imgur_link.setStyleSheet("border: 2px solid green; border-radius: 3px;")
            self.push_imgur_image.setDisabled(True)
            if config.imgurClose:
                self.close()
            return None
        except processing.requests.exceptions.ConnectionError as e:
            error_text = f"Connection error: {e}"
            self.push_imgur_link.setText(error_text)
            self.push_imgur_link.setStyleSheet("border: 2px solid red; border-radius: 3px;")
            return error_text
        except processing.NoLinkException as e:
            error_text = "Error: link is empty or invalid"
            self.push_link.setText(error_text)
            self.push_link.setStyleSheet("border: 2px solid red; border-radius: 3px;")
            return error_text

class EditConfig(QtWidgets.QWidget):
    __slots__ = ()

    def __init__(self):
        super().__init__()
        __screen = QtWidgets.QDesktopWidget().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)
        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), __screen_geo.width(), __screen_geo.left(), __screen_geo.top()
        self.setGeometry((self.left + (self.width / 2 - 200)), (self.top + (self.height / 2 - 180)), 400, 460)
        self.setFixedSize(400, 460)
        self.setWindowTitle("Configuration")
        self.initLayout()
        self.show()

    def initLayout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.shadows_config, self.custom_config, self.imgur_config = [
            QtWidgets.QGroupBox() for i in range(3)
        ]
        self.imgur_config.setTitle("Imgur")
        self.shadows_config.setTitle("Shadows")
        self.custom_config.setTitle("Custom upload")
        self.imgur_config.setStyleSheet(r"""
                QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        self.shadows_config.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        self.custom_config.setStyleSheet(r"""
        QGroupBox{border: 1px solid black;margin-top: 0.5em;font: 12px consolas;}QGroupBox::title {top: -7px;left: 10px;}""")
        #SHADOWS
        # shadows_v wraps shadows_h0, shadows_h1, shadows_h2, shadows_h3
        self.shadows_v = QtWidgets.QVBoxLayout()

        # h-n represent new row
        self.shadows_h0 = QtWidgets.QHBoxLayout()
        self.shadows_h1 = QtWidgets.QHBoxLayout()
        self.shadows_h2 = QtWidgets.QHBoxLayout()
        self.shadows_h3 = QtWidgets.QHBoxLayout()

        # shadows_h0 wraps free_space, free_space_label
        self.free_space = QtWidgets.QSpinBox()
        self.free_space.setRange(10, 240)
        self.free_space.setValue(config.userSpace)
        self.free_space.valueChanged[int].connect(self.changeFreeSpace)
        self.free_space_label = QtWidgets.QLabel("Offset from image:")

        # shadows_h1 wraps shadow_size, shadow_size_label
        self.shadow_size = QtWidgets.QSpinBox()
        self.shadow_size.setRange(1, 100)
        self.shadow_size.setValue(config.userShadowSize)
        self.shadow_size.valueChanged.connect(self.changeShadowSize)
        self.shadow_size_label = QtWidgets.QLabel("Shadow size:")

        # shadows_h2 wraps iterations, iterations_label
        self.iterations = QtWidgets.QSpinBox()
        self.iterations.setRange(1, 100)
        self.iterations.setValue(config.userIterations)
        self.iterations.valueChanged.connect(self.changeIterations)
        self.iterations_label = QtWidgets.QLabel("Shadow blur:")

        # shadows_h3 wraps draw_shadows, draw_shadows_label, round_corners, round_corners_label
        self.draw_shadows_label = QtWidgets.QLabel("Draw shadows by default:")
        self.draw_shadows = QtWidgets.QCheckBox()
        self.draw_shadows.setChecked(config.shadowDraw)
        self.draw_shadows.stateChanged.connect(self.changeShadowDraw)

        self.round_corners_label = QtWidgets.QLabel("Round image corners:")
        self.round_corners = QtWidgets.QCheckBox()
        self.round_corners.setChecked(config.roundCorners)
        self.round_corners.stateChanged.connect(self.changeRoundCorners)

        self.shadows_h0.addWidget(self.free_space_label)
        self.shadows_h0.addWidget(self.free_space)

        self.shadows_h1.addWidget(self.shadow_size_label)
        self.shadows_h1.addWidget(self.shadow_size)

        self.shadows_h2.addWidget(self.iterations_label)
        self.shadows_h2.addWidget(self.iterations)

        self.shadows_h3.addWidget(self.draw_shadows_label)
        self.shadows_h3.addWidget(self.draw_shadows)
        self.shadows_h3.addWidget(self.round_corners_label)
        self.shadows_h3.addWidget(self.round_corners)

        self.shadows_v.addLayout(self.shadows_h0)
        self.shadows_v.addLayout(self.shadows_h1)
        self.shadows_v.addLayout(self.shadows_h2)
        self.shadows_v.addLayout(self.shadows_h3)

        self.shadows_config.setLayout(self.shadows_v)

        #CUSTOM UPLOAD
        # custom_v wraps custom_h0, custom_h1, custom_h2, custom_h3, custom_h4, custom_h5
        self.custom_v = QtWidgets.QVBoxLayout()

        self.custom_h0, self.custom_h1, self.custom_h2, self.custom_h3, self.custom_h4, self.custom_h5 = [
            QtWidgets.QHBoxLayout() for i in range(0, 6)
        ]

        self.custom_access_token = QtWidgets.QLineEdit(config.userCustomAccessToken)
        self.custom_access_token.textChanged.connect(self.changeAPIKey)
        self.custom_access_token_label = QtWidgets.QLabel("Access token (in form 'headername MYTOKEN')")
        self.custom_access_token_description = QtWidgets.QLabel("Example: token yBj23soANO")

        self.custom_username = QtWidgets.QLineEdit(config.userCustomUsername)
        self.custom_username.textChanged.connect(self.changeCustomUsername)
        self.custom_username_label = QtWidgets.QLabel("Username:")

        self.custom_password = QtWidgets.QLineEdit(config.userCustomPassword)
        self.custom_password.textChanged.connect(self.changeCustomPassword)
        self.custom_password_label = QtWidgets.QLabel("Password:")

        self.custom_screenshot_name = QtWidgets.QSpinBox()
        self.custom_screenshot_name.setRange(0, 1)
        self.custom_screenshot_name.setValue(config.userCustomName)
        self.custom_screenshot_name.valueChanged.connect(self.changeScreenshotName)
        self.custom_screenshot_name_label = QtWidgets.QLabel("Send filename:")

        self.custom_link = QtWidgets.QLineEdit(config.userCustomLink)
        self.custom_link.textChanged.connect(self.changeCustomLink)
        self.custom_link_label = QtWidgets.QLabel("Custom link:")

        self.custom_h0.addWidget(self.custom_access_token_label, QtCore.Qt.AlignLeft)
        self.custom_h0.addWidget(self.custom_access_token, QtCore.Qt.AlignRight)

        self.custom_h1.addWidget(self.custom_access_token_description)

        self.custom_h2.addWidget(self.custom_username_label, QtCore.Qt.AlignLeft)
        self.custom_h2.addWidget(self.custom_username, QtCore.Qt.AlignRight)

        self.custom_h3.addWidget(self.custom_password_label, QtCore.Qt.AlignLeft)
        self.custom_h3.addWidget(self.custom_password, QtCore.Qt.AlignRight)

        self.custom_h4.addWidget(self.custom_screenshot_name_label, QtCore.Qt.AlignLeft)
        self.custom_h4.addWidget(self.custom_screenshot_name, QtCore.Qt.AlignRight)

        self.custom_h5.addWidget(self.custom_link_label, QtCore.Qt.AlignLeft)
        self.custom_h5.addWidget(self.custom_link, QtCore.Qt.AlignRight)

        self.custom_v.addLayout(self.custom_h0)
        self.custom_v.addLayout(self.custom_h1)
        self.custom_v.addLayout(self.custom_h2)
        self.custom_v.addLayout(self.custom_h3)
        self.custom_v.addLayout(self.custom_h4)
        self.custom_v.addLayout(self.custom_h5)

        self.custom_config.setLayout(self.custom_v)

        # IMGUR
        # imgur_v wraps imgur_h0, imgur_h1
        self.imgur_v = QtWidgets.QVBoxLayout()

        self.imgur_h0 = QtWidgets.QHBoxLayout()
        self.imgur_h1 = QtWidgets.QHBoxLayout()

        self.imgur_checkbox0 = QtWidgets.QCheckBox()
        self.imgur_checkbox0.setChecked(config.imgurClipboard)
        self.imgur_checkbox0.stateChanged.connect(self.changeImgurClipboard)

        self.imgur_checkbox1 = QtWidgets.QCheckBox()
        self.imgur_checkbox1.setChecked(config.imgurClose)
        self.imgur_checkbox1.stateChanged.connect(self.changeImgurClose)

        self.imgur_label_checkbox0 = QtWidgets.QLabel("Copy link to clipboard:")
        self.imgur_label_checkbox1 = QtWidgets.QLabel("Close on successful upload:")

        self.imgur_h0.addWidget(self.imgur_label_checkbox0)
        self.imgur_h0.addWidget(self.imgur_checkbox0)
        
        self.imgur_h1.addWidget(self.imgur_label_checkbox1)
        self.imgur_h1.addWidget(self.imgur_checkbox1)

        self.imgur_v.addLayout(self.imgur_h0)
        self.imgur_v.addLayout(self.imgur_h1)
        self.imgur_config.setLayout(self.imgur_v)

        self.layout.addWidget(self.shadows_config)
        self.layout.addWidget(self.custom_config)
        self.layout.addWidget(self.imgur_config)
        self.setLayout(self.layout)

    @QtCore.pyqtSlot()
    def changeFreeSpace(self):
        config.changeConfig("shadows", "space", self.free_space.value())

    def changeShadowSize(self):
        config.changeConfig("shadows", "shadow_space", self.shadow_size.value())

    def changeIterations(self):
        config.changeConfig("shadows", "iterations", self.iterations.value())
    
    def changeShadowDraw(self):
        config.changeConfig("shadows", "draw_default", int(self.draw_shadows.isChecked()))

    def changeRoundCorners(self):
        config.changeConfig("shadows", "round_corners", int(self.round_corners.isChecked()))
    
    def changeAPIKey(self):
        config.changeConfig("custom", "access_token", self.custom_access_token.text())
    
    def changeCustomUsername(self):
        config.changeConfig("custom", "username", self.custom_username.text())
    
    def changeCustomPassword(self):
        config.changeConfig("custom", "password", self.custom_password.text())
    
    def changeScreenshotName(self):
        if self.custom_screenshot_name.value() == 1:
            value = True
        else:
            value = False
        config.changeConfig("custom", "name", value)
    
    def changeCustomLink(self):
        config.changeConfig("custom", "link", self.custom_link.text())

    def changeImgurClipboard(self):
        if self.imgur_checkbox0.isChecked():
            self.imgur_checkbox1.setEnabled(True)
        else:
            self.imgur_checkbox1.setEnabled(False)
            config.changeConfig("imgur", "close_on_upload", 0)
            self.imgur_checkbox1.setChecked(False)
        config.changeConfig("imgur", "clipboard", int(self.imgur_checkbox0.isChecked()))

    def changeImgurClose(self):
        config.changeConfig("imgur", "close_on_upload", int(self.imgur_checkbox1.isChecked()))


class ReadConfig(QtWidgets.QWidget):
    __slots__ = ()

    def __init__(self):
        super().__init__()
        self.script_path = path.dirname(path.realpath(__file__))
        if path.isfile(f"{self.script_path}/config"):
            with open(f"{self.script_path}/config", "r") as file:
                self.data = file.read()
                self.parse = json.loads(self.data)
                self.initValues()
        else:
            with open(f"{self.script_path}/config", "w") as file:
                # sets default config if there is no such in script path
                self.parse = {"config": 
                {"shadows": {"space": 150, "shadow_space": 4, "iterations": 26, "draw_default": 0, "round_corners": 0}, 
                "custom": {"access_token": "None", "username": "None", "password": "None", "name": 1, 
                "link": "None"},
                "imgur": {"client_id": "25b4ba1ecc97502", "link": "https://api.imgur.com/3/image", 
                          "clipboard": 1, "close_on_upload": 0}}}
                file.write(str(json.dumps(self.parse)))
                self.initValues()

    def initValues(self):
        # get config values
        self.userSpace = self.parse["config"]["shadows"]["space"]
        self.userShadowSize = self.parse["config"]["shadows"]["shadow_space"]
        self.userIterations = self.parse["config"]["shadows"]["iterations"]
        self.shadowDraw = bool(self.parse["config"]["shadows"]["draw_default"])
        self.roundCorners = bool(self.parse["config"]["shadows"]["round_corners"])

        self.userCustomAccessToken = self.parse["config"]["custom"]["access_token"]
        self.userCustomUsername = self.parse["config"]["custom"]["username"]
        self.userCustomPassword = self.parse["config"]["custom"]["password"]
        self.userCustomName = self.parse["config"]["custom"]["name"]
        self.userCustomLink = self.parse["config"]["custom"]["link"]

        self.userImgurID = self.parse["config"]["imgur"]["client_id"]
        self.userImgurLink = self.parse["config"]["imgur"]["link"]
        self.imgurClose = bool(self.parse["config"]["imgur"]["close_on_upload"])
        self.imgurClipboard = bool(self.parse["config"]["imgur"]["clipboard"])

    def changeConfig(self, section, undersection, value):
        self.parse["config"][section][undersection] = value
        with open(f"{self.script_path}/config", "w") as file:
            towrite = str(json.dumps(self.parse))
            file.write(towrite)
        self.initValues()
         
if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("-s", "--screenshot", required=False, action='store_true',
    help="Take fullscreen shot, copy to clipboard. Use with -d to save image to the disk.")
    ap.add_argument("-d", "--directory", required=False,
    help="If used without -s, sets default directory to save a screenshot. This way, Enter and U hotkeys will copy/upload image AND save it to the path provided. If used with -s, saves fullscreen shot to the path provided.")
    ap.add_argument("-m", "--monitor", required=False,
    help="Select screen to grab. [-1, 0, 1, 2, n] Default: -1 (all screens)")
    args = vars(ap.parse_args())
    mon = -1 if not args["monitor"] else int(args["monitor"])
    if args["directory"]:
        processing.SHOTPATH[1] = f"{args['directory']}/{processing.SHOTNAME}"
    if args["screenshot"] == True and not args["directory"]:
        processing.scrot(screen=mon, path=processing.SHOTPATH[0])
        processing.call(["xclip", "-sel", "clip", "-t", "image/png", processing.SHOTPATH[0]])
        sleep(0.1)
        remove(processing.SHOTPATH[0])
    elif args["screenshot"] == True and args["directory"]:
        processing.scrot(screen=mon, path=processing.SHOTPATH[1])
    else:
        pid = str(getpid())
        pidfile = "/tmp/chizuhoru.pid"
        pidfile_exit = pidfile + ".exit"
        if path.isfile(pidfile_exit):
            sys.exit(0)
        try:
            if path.isfile(pidfile):
                try:
                    with open(pidfile, 'r') as testcheck:
                        kill(int(testcheck.read()), 0)
                except OSError:
                    remove(pidfile)
                else:
                    print(f"Another instance is running: {pid}")
                    with open(pidfile_exit, 'w') as file:
                        pass
                    sys.exit(0)
            with open(pidfile, 'w') as file:
                file.write(pid)
        except PermissionError as e:
            print(f"Error writing to '{pidfile}': {e}")
            sys.exit(1)
        try:
            app = QtWidgets.QApplication(sys.argv)
            config = ReadConfig()
            stayInTray = Tray()
            stayInTray.show()
            app.aboutToQuit.connect(app.deleteLater)
            sys.exit(app.exec_())
        finally:
            unlink(pidfile)
