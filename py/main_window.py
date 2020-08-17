from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QStylePainter, QStyleOption, QStyleOptionTab, QCheckBox, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QTabBar, QStyle, QLabel, QLineEdit, QFrame, QTabWidget
from PyQt5.QtWidgets import QPushButton, QComboBox
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtCore
import os

from datetime import datetime
from time import sleep

class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.West)

class ProxyStyle(QtWidgets.QProxyStyle):
    def drawControl(self, element, opt, painter, widget):
        if element == QStyle.CE_TabBarTabLabel:
            ic = self.pixelMetric(QStyle.PM_TabBarIconSize)
            r = QtCore.QRect(opt.rect)
            w =  0 if opt.icon.isNull() else opt.rect.width() + self.pixelMetric(QStyle.PM_TabBarIconSize)
            r.setHeight(opt.fontMetrics.width(opt.text) + w)
            r.moveBottom(opt.rect.bottom())
            opt.rect = r
        QtWidgets.QProxyStyle.drawControl(self, element, opt, painter, widget)

class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent, app, config, image_toolkit):
        super().__init__()
        self.app = app
        self.parent = parent
        self.config = config
        self.image_toolkit = image_toolkit

        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = __screen_geo.height(), \
                                                       __screen_geo.width(), \
                                                       __screen_geo.left(), \
                                                       __screen_geo.top()
        self.setGeometry((self.left + (self.width / 2 - 200)),
                         (self.top + (self.height / 2)),
                         600, 350)

        self.setFixedSize(600, 350)
        self.setWindowTitle("Chizuhoru")

        self.file_filter = 'png'
        self.typed_dir_hint_list = []

        self.initLayout()
    
    def initLayout(self):
        self.setStyle(ProxyStyle())
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabs = TabWidget()
        
        self.tab_capture, self.tab_upload, self.tab_settings, self.tab4 = [
            QtWidgets.QWidget() for i in range(4)
        ]
        
        self.tabs.addTab(self.tab_capture,"Capture")
        self.tabs.addTab(self.tab_upload,"Upload")
        self.tabs.addTab(self.tab_settings,"Settings")

        self.initTabCapture()
        self.initTabUpload()
        self.initTabSettings()
        
        self.tabs.setCurrentIndex(1)
        self.tabs.currentChanged.connect(self.capture_init)

        self.layout.addWidget(self.tabs)
        
        self.setLayout(self.layout)

    @QtCore.pyqtSlot()
    def capture_init(self):
        if self.tabs.currentIndex() == 0:
            self.setWindowOpacity(0)
            self.setFixedSize(0, 0)
            self.resize(0, 0)
            self.move(self.height, self.width)
            self.setVisible(False)
            self.close()
            sleep(self.parent.config.parse["config"]["default_delay"])
            self.parent.initCaptureCheck()

    def initTabCapture(self):
        pass
    
    def initTabUpload(self):
        main_v = QtWidgets.QVBoxLayout()

        inner_q_up = QFrame()
        inner_q_down = QFrame()
        inner_q_up.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        inner_q_down.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        inner_v_up = QVBoxLayout()

        in_hb_1 = QHBoxLayout()
        file_l = QLabel("File: ")

        self.ql_f = QComboBox()
        self.ql_f.setEditable(True)
        self.ql_f.setInsertPolicy(QComboBox.NoInsert)
        self.ql_f.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.ql_f.setMinimumWidth(340)
        self.ql_f.setDuplicatesEnabled(False)
        usr_dir = self.config.parse['config']['default_dir']
        if not usr_dir:
            usr_dir = os.environ['USER']
        self.update_file_box(usr_dir)
        self.ql_f.setCurrentIndex(-1)

        self.ql_f.currentTextChanged.connect(self.update_file_box_typing)

        self.ql_b = QPushButton("Browse")
        self.ql_b.clicked.connect(self.call_file_dialog)
        in_hb_1.addWidget(file_l)
        in_hb_1.addWidget(self.ql_f)
        in_hb_1.addWidget(self.ql_b)

        in_hb_2 = QHBoxLayout()
        in_hb_left = QVBoxLayout()
        in_hb_left_q = QFrame()

        copy_h = QHBoxLayout()
        self.copy_check = QCheckBox()
        self.copy_check.setChecked(bool(self.config.parse['config']['upload']['clipboard_state']))
        self.copy_check.stateChanged.connect(self.update_upload_copyclip_state)
        copy_lab = QLabel("Copy link after upload")
        copy_h.addWidget(self.copy_check)
        copy_h.addWidget(copy_lab)
        copy_h.addStretch(1)

        name_h = QHBoxLayout()
        self.name_check = QCheckBox()
        self.name_check.setChecked(bool(self.config.parse['config']['upload']['random_fname_state']))
        self.name_check.stateChanged.connect(self.update_upload_randname_state)
        name_lab = QLabel("Send random filename")
        name_h.addWidget(self.name_check)
        name_h.addWidget(name_lab)
        name_h.addStretch(1)

        in_hb_left.addStretch(1)
        in_hb_left.addItem(copy_h)
        in_hb_left.addItem(name_h)
        in_hb_left.addStretch(1)
        in_hb_left_q.setLayout(in_hb_left)

        tab_v = QtWidgets.QVBoxLayout()

        hb_left_tab = QTabWidget()
        tab_set = QtWidgets.QWidget()
        tab_v.addWidget(in_hb_left_q)
        tab_set.setLayout(tab_v)

        tab_up = QtWidgets.QWidget()
        in_hb_right = QVBoxLayout()

        self.up_btn = QPushButton("Upload")
        self.up_btn.clicked.connect(self.file_upload)

        up_hbox = QHBoxLayout()
        up_lab = QLabel("Service: ")
        self.up_comb = QComboBox()
        self.up_comb.addItem("Imgur")
        self.up_comb.addItem("catbox.moe")
        self.up_comb.addItem("uguu.se")
        up_hbox.addWidget(up_lab)
        up_hbox.addWidget(self.up_comb)
        in_hb_right.addItem(up_hbox)
        in_hb_right.addWidget(self.up_btn)

        tab_up.setLayout(in_hb_right)
        hb_left_tab.addTab(tab_up, "General")
        hb_left_tab.addTab(tab_set, "Settings")

        inner_q_res = QFrame()
        result_b = QVBoxLayout()
        self.result_f = QtWidgets.QTextEdit("")
        self.result_f.setFixedHeight(50)
        self.result_f.setReadOnly(True)
        self.result_f.setTextInteractionFlags(self.result_f.textInteractionFlags() \
                                              | Qt.TextSelectableByKeyboard)
        if self.parent.last_url:
            self.result_f.setText(self.parent.last_url)
        result_btn = QPushButton("Copy")
        result_btn.clicked.connect(self.copy_to_clipboard)
        result_b.addStretch(1)
        result_b.addWidget(self.result_f)
        result_b.addWidget(result_btn)

        inner_q_res.setLayout(result_b)

        in_hb_2.addWidget(hb_left_tab, 50)
        in_hb_2.addWidget(inner_q_res, 50)
        inner_v_up.addItem(in_hb_1)
        inner_v_up.addItem(in_hb_2)

        inner_v_down = QVBoxLayout()
        self.out = QtWidgets.QTextEdit("Idle")
        self.out.setReadOnly(True)
        self.out.setTextInteractionFlags(self.out.textInteractionFlags() \
                                         | Qt.TextSelectableByKeyboard)
        self.out.setStyleSheet(("QTextEdit { background-color: black; color: white; "
                                "border: 0; padding-left: 4px; padding-top: 4px;"
                                "font-family: monospace; }"))
        if self.parent.last_out:
            self.out.setText(self.parent.last_out)
        inner_v_down.addWidget(self.out)

        inner_q_up.setLayout(inner_v_up)
        inner_q_down.setLayout(inner_v_down)

        main_v.addWidget(inner_q_up, 30)
        main_v.addWidget(inner_q_down, 70)
        self.tab_upload.setLayout(main_v)

    def initTabSettings(self):
        main_wrap = QVBoxLayout()

        dir_lab = QLabel("Save directory: ")
        up_dir = QHBoxLayout()
        self.dirline = QLineEdit()
        self.dirline.setText(self.config.parse['config']['default_dir'])
        self.dirline.setReadOnly(True)
        self.dirbtn = QPushButton("Browse")
        self.dirbtn.clicked.connect(self.browse_directories)
        up_dir.addWidget(dir_lab)
        up_dir.addWidget(self.dirline)
        up_dir.addWidget(self.dirbtn)

        bot_left_fr = QFrame()
        bot_left_fr.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        bot_left = QVBoxLayout()
        bot_left_0 = QHBoxLayout()
        self.del_check = QtWidgets.QDoubleSpinBox()
        self.del_check.setSingleStep(0.05)
        self.del_check.setDecimals(2)
        del_lab = QLabel("Default delay (seconds): ")
        self.del_check.setValue(self.config.parse['config']['default_delay'])
        self.del_check.valueChanged.connect(self.update_delay)
        bot_left_0.addWidget(del_lab)
        bot_left_0.addWidget(self.del_check)
        bot_left_1 = QHBoxLayout()
        fmt_lab = QLabel("Name pattern: ")
        self.fmt_ql = QLineEdit()
        self.fmt_ql.setText(self.config.parse['config']['filename_format'])
        self.fmt_ql.textChanged.connect(self.update_file_format)
        bot_left_1.addWidget(fmt_lab)
        bot_left_1.addWidget(self.fmt_ql)
        bot_left_2 = QHBoxLayout()
        ico_lab = QLabel("Tray icon style: ")
        self.ico_comb = QComboBox()
        self.ico_comb.addItem("Colored")
        self.ico_comb.addItem("White")
        self.ico_comb.addItem("Black")
        curr_ico = self.config.parse['config']['icon']
        if curr_ico == 'white':
            self.ico_comb.setCurrentIndex(1)
        elif curr_ico == 'black':
            self.ico_comb.setCurrentIndex(2)
        self.ico_comb.currentIndexChanged.connect(self.update_ico)
        bot_left_2.addWidget(ico_lab)
        bot_left_2.addWidget(self.ico_comb)
        bot_left.addItem(up_dir)
        bot_left.addItem(bot_left_1)
        bot_left.addItem(bot_left_0)
        bot_left.addItem(bot_left_2)
        bot_left_fr.setLayout(bot_left)

        bot_right_fr = QFrame()
        bot_right = QVBoxLayout()
        bot_right_fr.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        bot_right_0 = QHBoxLayout()
        up_lab = QLabel("Upload button service: ")
        self.set_up_comb = QComboBox()
        self.set_up_comb.addItem("Imgur")
        self.set_up_comb.addItem("catbox.moe")
        self.set_up_comb.addItem("uguu.se")
        curr_serv = self.config.parse['config']['canvas']['upload_service']
        if curr_serv == 'catbox.moe':
            self.set_up_comb.setCurrentIndex(1)
        elif curr_serv == 'uguu.se':
            self.set_up_comb.setCurrentIndex(2)
        self.set_up_comb.currentIndexChanged.connect(self.update_canvas_upload)
        bot_right_0.addWidget(up_lab)
        bot_right_0.addWidget(self.set_up_comb)
        bot_right_1 = QHBoxLayout()
        save_lab = QLabel("Save button: ")
        self.set_save = QComboBox()
        self.set_save.addItem("Saves to default directory")
        self.set_save.addItem("Invokes save dialog")
        if self.config.parse['config']['canvas']['save_action'] == 'dialog':
            self.set_save.setCurrentIndex(1)
        self.set_save.currentIndexChanged.connect(self.update_canvas_save)
        bot_right_1.addWidget(save_lab)
        bot_right_1.addWidget(self.set_save)
        bot_right_2 = QHBoxLayout()
        img_clip_lab = QLabel("Copy image to clipboard on save")
        self.img_check = QCheckBox()
        self.img_check.setChecked(bool(self.config.parse['config']['canvas']['img_clip']))
        self.img_check.stateChanged.connect(self.update_img_clip)
        bot_right_2.addWidget(self.img_check)
        bot_right_2.addWidget(img_clip_lab)
        bot_right_2.addStretch(1)
        bot_right.addItem(bot_right_0)
        bot_right.addItem(bot_right_1)
        bot_right.addItem(bot_right_2)
        bot_right_fr.setLayout(bot_right)

        bot_wrap = QVBoxLayout()
        lab_0 = QLabel(" General")
        lab_1 = QLabel(" Paint window")
        lab_0.setFixedHeight(30)
        lab_1.setFixedHeight(30)
        bot_wrap.addWidget(lab_0)
        bot_wrap.addWidget(bot_left_fr)
        bot_wrap.addStretch(1)
        bot_wrap.addWidget(lab_1)
        bot_wrap.addWidget(bot_right_fr)
        
        main_wrap.addItem(bot_wrap)

        qw = QFrame()
        qw.setLayout(main_wrap)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(qw)

        scroll_wrap = QVBoxLayout()
        scroll_wrap.addWidget(scroll)
        self.tab_settings.setLayout(scroll_wrap)

    def closeEvent(self, event):
        self.parent.last_out = self.out.toPlainText()
        self.parent.last_url = self.result_f.toPlainText()
        self.close()

    def file_upload(self):
        get_file = self.ql_f.currentText().strip()
        if not os.path.isfile(get_file):
            if get_file:
                self.out.setText(f"File not found: {get_file}")
            return

        self.out.clear()
        self.result_f.clear()

        if self.up_comb.currentText() == 'Imgur':
            response_json = self.image_toolkit.imgur_upload(self.config,
                                                            get_file,
                                                            randname=self.name_check.isChecked(),
                                                            parent=self)
            if response_json:
                self.result_f.setText(response_json)
                if self.copy_check.isChecked():
                    self.copy_to_clipboard()
        elif self.up_comb.currentText() == 'catbox.moe':
            response = self.image_toolkit.catbox_upload(self.config,
                                                        get_file,
                                                        randname=self.name_check.isChecked(),
                                                        parent=self)
            if response:
                self.result_f.setText(response)
                if self.copy_check.isChecked():
                    self.copy_to_clipboard()
        else:
            response = self.image_toolkit.uguu_upload(self.config,
                                                      get_file,
                                                      randname=self.name_check.isChecked(),
                                                      parent=self)
            if response:
                self.result_f.setText(response)
                if self.copy_check.isChecked():
                    self.copy_to_clipboard()

    def browse_directories(self):
        filedialog = QtWidgets.QFileDialog()
        filedialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        filedialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        fd = filedialog.getExistingDirectory(self, 'Select directory')
        dirpath = fd if fd else None
        if dirpath and os.path.isdir(dirpath):
            self.dirline.setText(dirpath)
            self.config.changeConfig('default_dir', value=dirpath)

    def call_file_dialog(self):
        qdialog_filter = ('All files (*.*)'
                             ';;Pictures (*.png *.jpg *.jpeg *.bmp *.ico *.tiff)'
                             ';;Videos (*.mp4 *.webm *.mkv *.mov)'
                             ';;Text (*.txt)'
                          )
        if self.up_comb.currentData(self.up_comb.currentIndex()) == 'Imgur':
            qdialog_filter = 'Pictures (*.png *.jpg *.jpeg *.bmp *.ico *.tiff)'
        fd = QtWidgets.QFileDialog().getOpenFileName(self, 'Select file',
                                                     '', qdialog_filter)

        filepath = fd[0] if fd[0] else None
        if filepath:
            self.file_filter = fd[0].split('.')[1]
            last_dir = os.path.split(filepath)[0]
            self.ql_f.insertItem(0, filepath)
            self.ql_f.setCurrentIndex(0)
            self.update_file_box(last_dir)

    def update_file_box(self, usr_dir, signal='keep'):
        if signal == 'reset':
            # disconnect comboBox to avoid recursion
            self.ql_f.currentTextChanged.disconnect()
        else:
            curr_item = None
            if self.ql_f.currentText().strip():
                curr_item = self.ql_f.currentText().strip()
            self.ql_f.clear()
            if curr_item and os.path.isfile(curr_item):
                self.ql_f.addItem(curr_item)
                self.ql_f.setCurrentIndex(0)
        if os.path.isdir(usr_dir):
            files = [f for f in os.listdir(usr_dir) if os.path.isfile(os.path.join(usr_dir, f))]
            for f in files:
                if not f.startswith('.'):
                    if self.file_filter and f.endswith(self.file_filter):
                        check = self.ql_f.findText(os.path.join(usr_dir, f))
                        if check == -1:
                            self.ql_f.addItem(os.path.join(usr_dir, f))
                    elif not self.file_filter:
                        check = self.ql_f.findText(os.path.join(usr_dir, f))
                        if check == -1:
                            self.ql_f.addItem(os.path.join(usr_dir, f))
        if signal == 'reset':
            self.ql_f.currentTextChanged.connect(self.update_file_box_typing)

    def update_file_box_typing(self):
        filepath = self.ql_f.currentText().strip()
        if filepath:
            filedir = os.path.split(filepath)[0]
            if filedir in self.typed_dir_hint_list:
                return
            self.typed_dir_hint_list.append(filedir)
            if os.path.isdir(filedir):
                self.update_file_box(filedir, signal='reset')

    def copy_to_clipboard(self):
        value = self.result_f.toPlainText()
        if value.strip():
            self.app.clipboard().setText(value)

    def update_upload_copyclip_state(self):
        if self.copy_check.isChecked():
            self.config.changeConfig('upload', 'clipboard_state', 1)
        else:
            self.config.changeConfig('upload', 'clipboard_state', 0)

    def update_upload_randname_state(self):
        if self.name_check.isChecked():
            self.config.changeConfig('upload', 'random_fname_state', 1)
        else:
            self.config.changeConfig('upload', 'random_fname_state', 0)

    def update_delay(self):
        self.config.changeConfig('default_delay', value=self.del_check.value())

    def update_file_format(self):
        new_format = self.fmt_ql.text()
        self.config.changeConfig('filename_format', value=new_format)

    def update_canvas_upload(self):
        new = self.set_up_comb.currentText()
        self.config.changeConfig('canvas', 'upload_service', new)

    def update_canvas_save(self):
        new = self.set_save.currentText()
        if 'dialog' in new:
            new = 'dialog'
        else:
            new = 'dir'
        self.config.changeConfig('canvas', 'save_action', new)

    def update_img_clip(self):
        if self.img_check.isChecked():
            self.config.changeConfig('canvas', 'img_clip', 1)
        else:
            self.config.changeConfig('canvas', 'img_clip', 0)

    def update_ico(self):
        new_ico = self.ico_comb.currentText()
        self.config.changeConfig('icon', value=new_ico.lower())