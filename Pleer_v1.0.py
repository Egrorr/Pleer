import sys, os, random, requests
from time import time
import pygame as pg
from downloader import download
from getinfo import Searcher
from itertools import groupby
from multiprocessing import Process, active_children, freeze_support
from PyQt5.QtWidgets import QApplication, QToolBar, QFileDialog, QAbstractItemView, QInputDialog, QHBoxLayout, \
    QMainWindow, QAction, QMessageBox, QListWidgetItem, QWidget, QPushButton, QCheckBox, QColorDialog, QMenu
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QColor, QPixmap, QIcon, QImage, QFont, QLinearGradient, QPalette, QBrush


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def searchf(direct, mainobj):
    global db
    tl1 = []
    os.chdir(mainobj.workdirect)
    try:
        line = readfile("links.txt", strind=0)
    except FileNotFoundError:
        with open(filespath["links.txt"], mode="w+", encoding="utf-8") as f:
            f.write('')
        line = readfile("links.txt", strind=0)
    if not line:
        db = {}
    else:
        db = eval(line)
    for rootdir, dirs, files in os.walk(direct):
        for file in files:
            if file.split('.')[-1] in mainobj.extes:
                tl1.append(file)
                db[file] = rootdir
    with open(filespath["links.txt"], mode="w", encoding="utf-8") as f:
        f.write(str(db))
    return tl1


def get_filespath():
    return {
        'links.txt': 'config/links.txt',
        'music_direction.txt': 'config/music_direction.txt',
        'playlists.txt': 'config/playlists.txt',
        'tracksvolume.txt': 'config/tracksvolume.txt',
        'main': 'ui_source/main.ui',
        'edtpldiaog': 'ui_source/edtpldialog.ui',
        'edtfolddialog': 'ui_source/edtfloddialog.ui',
        'main.css': 'ui_source/main.css',
        'dandd.css': 'ui_source/dandd.css',
        'edit.css': 'ui_source/edit.css',
        'gradient.txt': 'config/gradient.txt',
        'mainicon2.jpg': 'decor_source/mainicon2.jpg',
        'editicon.jpg': 'decor_source/editicon.jpg',
        'danddicon.jpg': 'decor_source/danddicon.jpg',
        'none.png': 'decor_source/none.png',
        'stylesheetedt.png': 'decor_source/stylesheetedt.png',
        'stylessheetedt.css': 'ui_source/stylesheetedt.css',
        'filespath.txt': 'config/filespath.txt'
    }


def checkforrepeat(mainobj):
    repeatfl = [tx for i, tx in enumerate(mainobj.allfiles) if i != mainobj.allfiles.index(tx)]
    links = eval(readfile("links.txt", strind=0))
    for track in repeatfl:
        os.remove(f'{links[track]}/{track}')
    mainobj.allfiles = [i for i, _ in groupby(mainobj.allfiles)]


def readfile(filename, strind=-1):
    with open(filespath[filename], mode="r", encoding="utf-8") as f:
        lines = f.readlines()
    if strind == -1:
        return lines
    elif strind == 0:
        with open(filespath[filename], mode="r", encoding="utf-8") as f:
            return f.readline()
    elif strind == -2:
        with open(filespath[filename], mode="r", encoding="utf-8") as f:
            return f.read()
    else:
        return lines[strind]


def clearfile(filename):
    with open(filespath[filename], mode="w+", encoding="utf-8") as f:
        f.write('')


def createvolume(wdirect, mainobj):
    os.chdir(wdirect)
    tracks = mainobj.allfiles
    try:
        lines = readfile("tracksvolume.txt", strind=-1)
    except FileNotFoundError:
        with open(filespath["tracksvolume.txt"], mode="w+", encoding="utf-8") as f:
            f.write('')
        lines = readfile("tracksvolume.txt", strind=-1)
    linestracks = []
    for i in lines:
        linestracks.append(i[:i.find(':')])
    if tracks != linestracks:
        for i in tracks:
            if i not in linestracks:
                with open(filespath["tracksvolume.txt"], mode="a+", encoding="utf-8") as f:
                    f.write(f'{i}: {1.0}\n')


def settrackvolume(trackname, volume):
    os.chdir(ex.workdirect)
    lines = readfile("tracksvolume.txt", strind=-1)
    reslines = []
    for i in lines:
        if trackname not in i[:i.index(':')]:
            reslines.append(i)
        else:
            reslines.append(f'{trackname}: {volume}\n')
    with open(filespath["tracksvolume.txt"], mode="w", encoding="utf-8") as f:
        f.writelines(reslines)


def item_render(i, text, adding=False, deleting=False, md=True, editing=False, img_url=False, dlgobj='', mainobj='',
                listwidget=1, inserting=False, others=True, setimage=True):
    item = QListWidgetItem()
    item.setText(text)
    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
    if img_url:
        item.setFont(QFont('Arial', 18))
        item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
    item_widget = QWidget()
    if not setimage:
        item_widget.setStyleSheet(f"background: {text};")
    item_layout = QHBoxLayout()
    if adding and md and others:
        if not img_url:
            item_buttonadd = QPushButton()
            if 'ui_source/edit.css' in filespath['edit.css']:
                item_buttonadd.setIcon(QIcon('decor_source/add.png'))
                item_buttonadd.setIconSize(QSize(25, 25))
                item_buttonadd.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
            item_buttonadd.setObjectName(f'tr_add_{i}')
            item_buttonadd.clicked.connect(mainobj.clickedaddinpl)
            item_layout.addWidget(item_buttonadd)
            item_layout.setAlignment(Qt.AlignRight)
        else:
            image = QImage()
            image.loadFromData(requests.get(img_url).content)
            item_buttondwn = QPushButton()
            if 'ui_source/dandd.css' in filespath['dandd.css']:
                item_buttondwn.setIcon(QIcon('decor_source/download.png'))
                item_buttondwn.setIconSize(QSize(50, 50))
                item_buttondwn.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
            item_buttondwn.setFont(QFont('Arial', 15))
            item_buttondwn.setObjectName(f'tr_dwn_{i}')
            item_buttondwn.clicked.connect(dlgobj.clickedaddinpl)
            image_icon = QIcon()
            image_icon.addPixmap(QPixmap(image))
            item.setIcon(image_icon)
            item_layout.addWidget(item_buttondwn)
            item_layout.setAlignment(Qt.AlignRight)
    elif adding and not md and others:
        item_buttonpass = QPushButton()
        if 'ui_source/edit.css' in filespath['edit.css']:
            item_buttonpass.setIcon(QIcon('decor_source/alreadyinplaylist.png'))
            item_buttonpass.setIconSize(QSize(25, 25))
            item_buttonpass.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
        item_buttonpass.setObjectName(f'passing{i}')
        item_layout.addWidget(item_buttonpass)
        item_layout.setAlignment(Qt.AlignRight)
    elif deleting and others:
        item_buttondel = QPushButton()
        if 'ui_source/edit.css' in filespath['edit.css']:
            item_buttondel.setIcon(QIcon('decor_source/deletefromplaylist.png'))
            item_buttondel.setIconSize(QSize(25, 25))
            item_buttondel.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
        item_buttondel.setObjectName(f'tr_del_{i}')
        item_buttondel.clicked.connect(mainobj.clickeddelinpl)
        item_layout.addWidget(item_buttondel)
        item_layout.setAlignment(Qt.AlignRight)
    elif deleting and not others:
        if setimage:
            item_buttondel = QPushButton()
            if 'ui_source/dandd.css' in filespath['dandd.css']:
                item_buttondel.setIcon(QIcon('decor_source/deletefromdevice.png'))
                item_buttondel.setIconSize(QSize(25, 25))
                item_buttondel.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
        else:
            item_buttondel = QPushButton('delete')
        item_buttondel.setObjectName(f'tr_del_{i}')
        item_buttondel.clicked.connect(dlgobj.clickeddelinpl)
        item_layout.addWidget(item_buttondel)
        item_layout.setAlignment(Qt.AlignRight)
    elif editing and i != 0 and others:
        item_buttonedt = QPushButton()
        if 'ui_source/main.css' in filespath['main.css']:
            item_buttonedt.setIcon(QIcon('decor_source/edit.png'))
            item_buttonedt.setIconSize(QSize(25, 25))
            item_buttonedt.setStyleSheet("background: rgba(0, 0, 0, 0); outline: none;")
        item_buttonedt.setObjectName(f'pl_cha_{i}')
        item_buttonedt.clicked.connect(mainobj.playlistchanging)
        item_layout.addWidget(item_buttonedt)
        item_layout.setAlignment(Qt.AlignRight)
    item_widget.setLayout(item_layout)
    item.setSizeHint(item_layout.sizeHint())
    if img_url:
        item.setSizeHint(QSize(360, 202))
    if mainobj.sch3 % 2 == 0:
        if 'ui_source/main.css' in filespath['main.css']:
            item.setBackground(QColor('#423357'))
        else:
            item.setBackground(QColor('gray'))
    else:
        if 'ui_source/main.css' in filespath['main.css']:
            item.setBackground(QColor('#473862'))
        else:
            item.setBackground(QColor('darkgray'))
    mainobj.sch3 += 1
    if listwidget == 1 and text and others:
        mainobj.listWidget.addItem(item)
        mainobj.listWidget.setItemWidget(item, item_widget)
    elif listwidget == 1 and text and not others:
        dlgobj.listWidget.addItem(item)
        dlgobj.listWidget.setItemWidget(item, item_widget)
    elif listwidget == 2 and text:
        mainobj.listWidget_2.addItem(item)
        mainobj.listWidget_2.setItemWidget(item, item_widget)
    elif listwidget == 3 and not inserting and text:
        dlgobj.listWidget_3.addItem(item)
        dlgobj.listWidget_3.setItemWidget(item, item_widget)
    elif listwidget == 3 and inserting and text:
        dlgobj.listWidget_3.insertItem(i, item)
        dlgobj.listWidget_3.setItemWidget(item, item_widget)
    elif listwidget == 4 and text:
        dlgobj.listWidget_4.addItem(item)
        dlgobj.listWidget_4.setItemWidget(item, item_widget)


def changelistdialog(playlist):
    global dlg
    dlg = PlaylistChangingDialog(playlist)
    with open(filespath['edit.css'], mode="r") as f:
        dlg.setStyleSheet(f.read())
    dlg.show()


def deletedownloadact():
    global addanddelldlg
    addanddelldlg = LoadAndDeletingDialog()
    with open(filespath['dandd.css'], mode="r") as f:
        addanddelldlg.setStyleSheet(f.read())
    addanddelldlg.show()


def stylesheetedtact():
    global ssedact
    ssedact = StyleSheetEdit()
    ssedact.show()


def recreatefile(mainobj):
    clearfile("music_direction.txt")
    os.chdir(mainobj.workdirect)
    with open(filespath["music_direction.txt"], mode="a+", encoding="utf-8") as f:
        f.write(f'music_direct: {os.getcwd()}\n')
        f.write(f'saving_direct: {mainobj.workdirect}/mus1_\n')
        mainobj.direct = os.getcwd()


class StyleSheetEdit(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui_source/stylesheetedt.ui', self)
        self.centralwidget.setLayout(self.verticalLayout)
        self.setWindowTitle('Style Edit')
        colors = eval(readfile("gradient.txt", strind=0))
        wrap(self, 'stylesheetedt.png', colors)
        self.logic()

    def logic(self):
        self.pushButton_14.clicked.connect(self.closing)
        self.pushButton_12.clicked.connect(self.colorpick)
        self.pushButton_15.clicked.connect(self.update2)
        self.pushButton_13.clicked.connect(self.save)
        self.stylesheetedtbtn = QPushButton('Download stylesheet(*.css)')
        self.stylesheetedtbtn.setObjectName('stylesheetedtbtn')
        menu = QMenu()
        menu.addAction(filespath['main.css'], self.setsstomain)
        menu.addAction(filespath['edit.css'], self.setsstoedit)
        menu.addAction(filespath['dandd.css'], self.setsstodandd)
        menu.addAction(filespath['stylessheetedt.css'], self.setsstossedt)
        self.stylesheetedtbtn.setMenu(menu)
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addWidget(self.stylesheetedtbtn)
        self.colors = eval(readfile("gradient.txt", strind=0))
        self.listWidget.setDragEnabled(True)
        self.listWidget.setAcceptDrops(True)
        self.listWidget.clear()
        [item_render(i, tx, deleting=True, mainobj=ex, dlgobj=self, others=False, listwidget=1, setimage=False) for
         i, tx in enumerate(self.colors)]

    def savenewstyle(self, name):
        global filespath
        filename = QFileDialog.getOpenFileName(self, 'Open file', None, "(*.css)")[0]
        line = eval(readfile("filespath.txt", strind=-2))
        line[f'{name}.css'] = filename
        filespath = line
        with open("config/filespath.txt", mode="w+", encoding="utf-8") as f:
            f.write(str(line))

    def setsstomain(self):
        self.savenewstyle('main')
        with open(filespath['main.css'], mode="r") as f:
            app.setStyleSheet(f.read())

    def setsstoedit(self):
        self.savenewstyle('edit')
        with open(filespath['edit.css'], mode="r") as f:
            dlg.setStyleSheet(f.read())

    def setsstodandd(self):
        self.savenewstyle('dandd')
        with open(filespath['dandd.css'], mode="r") as f:
            addanddelldlg.setStyleSheet(f.read())

    def setsstossedt(self):
        self.savenewstyle('stylesheetedt')
        with open(filespath['stylesheetedt.css'], mode="r") as f:
            ssedact.setStyleSheet(f.read())

    def save(self):
        with open(filespath["gradient.txt"], mode="w+", encoding="utf-8") as f:
            f.write(f'{self.colors}')
        wrap(ex, 'mainicon2.jpg', self.colors)
        wrap(self, 'stylesheetedt.png', self.colors)

    def update2(self):
        self.colors = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
        self.listWidget.clear()
        [item_render(i, tx, deleting=True, mainobj=ex, dlgobj=self, others=False, listwidget=1, setimage=False) for
         i, tx in enumerate(self.colors)]

    def colorpick(self):
        newcolor = QColorDialog.getColor()
        self.colors.append(newcolor.name())
        self.listWidget.clear()
        [item_render(i, tx, deleting=True, mainobj=ex, dlgobj=self, others=False, listwidget=1, setimage=False) for
         i, tx in enumerate(self.colors)]

    def closing(self):
        self.close()

    def clickeddelinpl(self):
        ind = int(self.sender().objectName()[7:])
        del self.colors[ind]
        self.listWidget.clear()
        [item_render(i, tx, deleting=True, mainobj=ex, dlgobj=self, others=False, listwidget=1, setimage=False) for
         i, tx in enumerate(self.colors)]


class LoadAndDeletingDialog(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui_source/edtfloddialog.ui', self)
        self.stateofwarningdlg = 0
        if readfile("gradient.txt", strind=0) == '':
            with open(filespath["gradient.txt"], mode="w", encoding="utf-8") as f:
                f.write("['#08465f', '#480644', '#2e3060']")
        colors = eval(readfile("gradient.txt", strind=0))
        wrap(self, 'danddicon.jpg', colors)
        self.logic()

    def logic(self):
        self.centralwidget.setLayout(self.verticalLayout_2)
        self.tabWidget.currentChanged.connect(self.changed)
        [item_render(i, tx, listwidget=4, mainobj=ex, dlgobj=self, deleting=True, others=False) for i, tx in
         enumerate(ex.allfiles)]
        self.tracklistnme = [self.listWidget_4.item(i).text() for i in range(self.listWidget_4.count())]
        self.pushButton_10.clicked.connect(self.closing)
        self.quit = QAction("Quit", self)
        self.setWindowTitle('Downloading & Deleting')
        self.quit.triggered.connect(self.closeEvent)
        self.addAction(self.quit)
        self.pushButton.clicked.connect(self.searchigbybtn)
        self.lineEdit.textChanged.connect(self.searchig)
        self.pushButton_10.clicked.connect(self.closing)
        self.savedirectchangebtn = QPushButton('Change saving directory')
        self.savedirectchangebtn.setObjectName('savedirectchangebtn')
        self.savedirectchangebtn.clicked.connect(self.savedirectchangeact)
        self.updatefilebtn = QPushButton('Update')
        self.updatefilebtn.setObjectName('updatefilebtn')
        self.updatefilebtn.clicked.connect(self.updatefileact)
        self.delwarningdialogbtn = QCheckBox('Hide warning of track deleting')
        self.delwarningdialogbtn.setObjectName('delwarningdialogbtn')
        self.delwarningdialogbtn.stateChanged.connect(self.delwarningdialogact)
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        self.toolBar.addWidget(self.savedirectchangebtn)
        self.toolBar.addWidget(self.updatefilebtn)
        self.toolBar.addWidget(self.delwarningdialogbtn)
        self.listWidget_3.setAttribute(Qt.WA_TranslucentBackground)

    def updatefileact(self):
        ex.changedflag = True
        self.changed()

    def delwarningdialogact(self):
        self.stateofwarningdlg = self.sender().checkState()

    def savedirectchangeact(self):
        drct = QFileDialog.getExistingDirectory(self, 'Directory', '/home')
        if drct != 'drct':
            os.chdir(ex.workdirect)
            lines = readfile("music_direction.txt", strind=-1)
            clearfile("music_direction.txt")
            with open(filespath["music_direction.txt"], mode="a+", encoding="utf-8") as f:
                for i in lines:
                    if 'saving_direct' not in i:
                        f.write(i)
                    else:
                        f.write(f'saving_direct: {drct}')

    def changed(self):
        ind = self.tabWidget.currentIndex()
        if ind == 1:
            if ex.changedflag is True:
                self.listWidget_4.clear()
                checkforrepeat(ex)
                ex.allfiles = searchf(ex.direct, ex)
                [item_render(i, tx, listwidget=4, mainobj=ex, dlgobj=self, deleting=True, others=False) for i, tx in
                 enumerate(ex.allfiles)]
                self.tracklistnme = [self.listWidget_4.item(i).text() for i in range(self.listWidget_4.count())]
                ex.changedflag = False

    def clickeddelinpl(self):
        if self.stateofwarningdlg == 0:
            msg = QMessageBox()
            msg.setStyleSheet("background-color: #372747; color: white; font: 14px bold")
            msg.setText('Are you sure about that?')
            msg.setWindowTitle('Track deleting')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setStyleSheet("background-color: #372747; color: white; font: 14px bold")
            ans = msg.exec_()
        else:
            ans = 16384
        if ans == 16384:  # why 16384 = Yes; 65536 = No?
            pg.mixer.music.stop()
            line = readfile("links.txt", strind=0)
            ind = int(self.sender().objectName()[7:])
            track = self.tracklistnme[ind]
            lines = readfile("playlists.txt", strind=-1)
            os.chdir(ex.workdirect)
            clearfile("playlists.txt")
            with open(filespath["playlists.txt"], mode="a+", encoding="utf-8") as f:
                for i in lines:
                    if track not in i:
                        f.write(i)
                    else:
                        muslist = eval('[' + i[i.find('['):][1:-2] + ']')
                        ind2 = muslist.index(track)
                        del muslist[ind2]
                        f.write(f"'{i[1:i.index(':') - 1]}': {str(muslist)}\n")
            currentnmes = [self.listWidget_4.item(i).text() for i in range(self.listWidget_4.count())]
            self.listWidget_4.takeItem(currentnmes.index(track))
            ex.changedflag = True
            checkforrepeat(ex)
            os.remove(f'{eval(line)[track]}/{track}')

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.searchigbybtn()

    def clickedaddinpl(self):
        ind = int(self.sender().objectName()[7:])
        url = srobj.urls[ind]
        os.chdir(ex.workdirect)
        file = readfile("music_direction.txt", strind=1)
        if 'mus1_' in file:
            file = file[15:-6]
        else:
            file = file[15:]
        dwnlp = Process(target=download, args=(url, file))
        dwnlp.start()

    def searchig(self):
        keyword = self.lineEdit.text()
        if self.tabWidget.currentIndex() == 1:
            self.listWidget_4.clear()
            [item_render(i, tx, mainobj=ex, dlgobj=self, listwidget=4, deleting=True, others=False) for i, tx in
             enumerate(ex.allfiles) if keyword.lower() in tx.lower()]

    def searchigbybtn(self):
        global srobj
        if self.tabWidget.currentIndex() == 0:
            self.listWidget_3.clear()
            self.listWidget_3.setIconSize(QSize(ex.normalsize[0], ex.normalsize[1]))
            self.listWidget_3.setWordWrap(True)
            keyword = self.lineEdit.text()
            srobj = Searcher(keyword, self.spinBox.value())
            [item_render(i, srobj.names[i], mainobj=ex, dlgobj=self, adding=True, listwidget=3,
                         img_url=srobj.thumbnailsurls[i]) for i in range(len(srobj.names))]
        elif self.tabWidget.currentIndex() == 1:
            self.searchig()

    def closing(self):
        self.close()
        ex.changedflag = True

    def closeEvent(self, event):
        self.closing()


class PlaylistChangingDialog(QMainWindow):
    def __init__(self, playlist):
        super().__init__()
        uic.loadUi('ui_source/edtpldialog.ui', self)
        ex.changingpl = playlist
        if readfile("gradient.txt", strind=0) == '':
            with open(filespath["gradient.txt"], mode="w", encoding="utf-8") as f:
                f.write("['#08465f', '#480644', '#2e3060']")
        colors = eval(readfile("gradient.txt", strind=0))
        wrap(self, 'editicon.jpg', colors)
        self.setWindowIcon(QIcon('decor_source/editicon.jpg'))
        self.centralwidget.setLayout(self.verticalLayout)
        self.playlist = playlist
        self.setWindowTitle(f'Editing: {playlist}')
        self.tabWidget.setTabText(0, 'Adding')
        self.tabWidget.setTabText(1, 'Deleting')
        self.pushButton_7.clicked.connect(self.playlistdel)
        self.pushButton.clicked.connect(self.extdialog)
        self.pushButton_9.clicked.connect(self.renamedialog)
        self.lineEdit.textChanged.connect(self.searching)
        self.listWidget_3.clear()
        os.chdir(ex.workdirect)
        lines = readfile("playlists.txt", strind=-1)
        for i in lines:
            if self.playlist in i[:i.index(':')]:
                tracks = eval('[' + i[i.find('['):][1:-2] + ']')
        [item_render(i, tx, adding=True, mainobj=ex, dlgobj=self, listwidget=3) if tx not in tracks else item_render(i,
                                                                                                                     tx,
                                                                                                                     adding=True,
                                                                                                                     md=False,
                                                                                                                     mainobj=ex,
                                                                                                                     dlgobj=self,
                                                                                                                     listwidget=3)
         for
         i, tx in enumerate(ex.allfiles)]
        self.tabWidget.currentChanged.connect(self.changed)
        tdir = os.getcwd()
        os.chdir(ex.workdirect)
        os.chdir(tdir)

    def changed(self):
        current = self.tabWidget.currentIndex()
        checkforrepeat(ex)
        tfiles = ex.allfiles
        os.chdir(ex.workdirect)
        lines = readfile("playlists.txt", strind=-1)
        for i in lines:
            if ex.changingpl in i[:i.index(':')]:
                tracks = eval('[' + i[i.find('['):][1:-2] + ']')
        if current == 0:
            if ex.changedflag is True:
                self.listWidget_3.clear()
                [item_render(i, tx, adding=True, mainobj=ex, dlgobj=self,
                             listwidget=3) if tx not in tracks else item_render(i, tx, adding=True, md=False,
                                                                                mainobj=ex, dlgobj=self, listwidget=3)
                 for i, tx in enumerate(tfiles)]
                ex.changedflag = False
        elif current == 1:
            self.listWidget_4.clear()
            [item_render(i, tx, deleting=True, listwidget=4, mainobj=ex, dlgobj=self) for i, tx in enumerate(tracks)]
            self.item_names = [self.listWidget_4.item(i).text() for i in range(self.listWidget_4.count())]

    def searching(self):
        keyword = self.lineEdit.text()
        current = self.tabWidget.currentIndex()
        if keyword != '':
            lines = readfile("playlists.txt", strind=-1)
            for i in lines:
                if self.playlist in i[:i.index(':')]:
                    tracks = eval(i[i.find(':') + 2:])
            if current == 0:
                self.listWidget_3.clear()
                for i, tx in enumerate(ex.allfiles):
                    if (tx not in tracks) and (keyword.lower() in tx.lower()):
                        item_render(i, tx, adding=True, md=True, mainobj=ex, dlgobj=self, listwidget=3)
            else:
                self.listWidget_4.clear()
                for i, tx in enumerate(tracks):
                    if keyword.lower() in tx.lower():
                        item_render(i, tx, deleting=True, listwidget=4, mainobj=ex, dlgobj=self)
        else:
            lines = readfile("playlists.txt", strind=-1)
            for i in lines:
                if self.playlist in i[:i.index(':')]:
                    tracks = eval('[' + i[i.find('['):][1:-2] + ']')
            dlg.listWidget_4.clear()
            dlg.listWidget_3.clear()
            [item_render(i, tx, deleting=True, listwidget=4, mainobj=ex, dlgobj=self) for i, tx in enumerate(tracks)]
            [item_render(i, tx, adding=True, mainobj=ex, dlgobj=self,
                         listwidget=3) if tx not in tracks else item_render(i, tx, adding=True, md=False, mainobj=ex,
                                                                            dlgobj=self, listwidget=3)
             for i, tx in enumerate(ex.allfiles)]

    def playlistdel(self):
        msgBox = QMessageBox()
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setText('Are you sure about that?')
        result = msgBox.exec_()
        if QMessageBox.Yes == result:
            pg.mixer.music.stop()
            os.chdir(ex.workdirect)
            lines = readfile("playlists.txt", strind=-1)
            clearfile("playlists.txt")
            os.chdir(ex.workdirect)
            with open(filespath["playlists.txt"], mode="a", encoding="utf-8") as f:
                for i in lines:
                    if ex.changingpl not in i[:i.index(':')]:
                        f.write(i)
                    else:
                        pass
        ex.listWidget_2.clear()
        os.chdir(ex.workdirect)
        lines = readfile("playlists.txt", strind=-1)
        lines = [i[:i.find('[') - 2][1:-1] for i in lines]
        [item_render(i, tx, mainobj=ex, listwidget=2, editing=True) for i, tx in enumerate(lines)]
        allp = eval(readfile("playlists.txt", strind=0)[7:])
        lines = readfile("playlists.txt")
        ex.activenme = None
        ex.activeplst = 'all'
        ex.filesnme = allp
        ex.stopedk = 0
        ex.listfiles = [ex.listWidget_2.item(i) for i in range(ex.listWidget_2.count())]
        ex.lists = [i[:i.find('[') - 2][1:-1] for i in lines]
        ex.activeplstitem = ex.listfiles[ex.lists.index('all')]
        self.closing()

    def renamedialog(self):
        newname, pressed = QInputDialog.getText(ex, 'New Playlist', 'Playlist Name:')
        lines = readfile("playlists.txt", strind=-1)
        plnames = [i[1:i.index(':') - 1] for i in lines]
        k = True
        while (newname in plnames or newname == '') and (pressed != QInputDialog.Rejected):
            err = QMessageBox.critical(ex, 'Incorrect Name', 'Enter another name',
                                       buttons=QMessageBox.Yes | QMessageBox.No)
            if err == QMessageBox.Yes:
                newname, pressed = QInputDialog.getText(ex, 'New Playlist', 'Playlist Name:')
            else:
                k = False
                break
        if newname not in ex.lists and k and pressed != QInputDialog.Rejected:
            clearfile("playlists.txt")
            os.chdir(ex.workdirect)
            with open(filespath["playlists.txt"], mode="a", encoding="utf-8") as f:
                for i in lines:
                    if ex.changingpl not in i[:i.index(':')]:
                        f.write(i)
                    else:
                        f.write(f"'{newname}': {i[i.index(':') + 2:]}")
        lines = readfile("playlists.txt", strind=-1)
        plnames = [i[1:i.index(':') - 1] for i in lines]
        allp = eval(readfile("playlists.txt", strind=0)[7:])
        ex.listWidget_2.clear()
        [item_render(i, tx, mainobj=ex, listwidget=2, editing=True) for i, tx in enumerate(plnames)]
        ex.activenme = allp[0]
        ex.activeplst = 'all'
        ex.filesnme = allp
        ex.stopedk = 0
        ex.changingpl = newname
        ex.listfiles = [ex.listWidget_2.item(i) for i in range(ex.listWidget_2.count())]
        ex.lists = [i[:i.find('[') - 2][1:-1] for i in lines]
        ex.activeplstitem = ex.listfiles[ex.lists.index('all')]
        dlg.setWindowTitle(f'Editing: {ex.changingpl}')

    def extdialog(self):
        self.closing()

    def closing(self):
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui_source/main.ui', self)
        pg.init()
        pth = os.getcwd().replace('\\', '/') + '/config/gradient.txt'
        if not os.path.exists(pth):
            clearfile("gradient.txt")
            with open(filespath["gradient.txt"], mode="w", encoding="utf-8") as f:
                f.write("['#08465f', '#480644', '#2e3060']")
        if readfile("gradient.txt", strind=0) == '':
            with open(filespath["gradient.txt"], mode="w", encoding="utf-8") as f:
                f.write("['#08465f', '#480644', '#2e3060']")
        colors = eval(readfile("gradient.txt", strind=0))
        wrap(self, 'mainicon2.jpg', colors)
        self.setWindowTitle('Pleer_v1.0')
        self.centralwidget.setLayout(self.formLayout)
        self.activenme = None
        self.activeitem = None
        self.activeplstitem = None
        self.activeplst = 'all'
        self.prevactplst = None
        self.log = set()
        self.normalsize = (360, 192)
        self.extes = ('ogg', 'mp3', 'wav')  # 32-битные wav-файлы не воспроизводятся на pg.mixer
        self.workdirect = os.getcwd()
        try:
            line = readfile("music_direction.txt", strind=0)
            self.direct = line[line.index(':') + 2:-1]
        except FileNotFoundError:
            recreatefile(self)
        except ValueError:
            recreatefile(self)
        file = ' '.join(readfile("music_direction.txt", strind=-1))
        if 'saving_direct' not in file or 'music_direct' not in file:
            recreatefile(self)
        self.allfiles = searchf(self.direct, self)
        checkforrepeat(self)
        self.time = -1
        self.sch1 = 2
        self.sch2 = 2
        self.sch3 = 2
        self.sch4 = 2
        self.f = True
        self.l = True
        self.changedflag = False
        self.files = []
        self.filesnme = []
        self.prev = 0
        self.stopedk = 0
        self.logic()

    def logic(self):
        self.listWidget.itemClicked.connect(self.oneclicktracks)
        self.horizontalSlider.sliderReleased.connect(self.chtme)
        self.pushButton.clicked.connect(self.pause)
        self.pushButton_3.clicked.connect(self.nexttr)
        self.pushButton_2.clicked.connect(self.previous)
        self.radioButton_2.toggled.connect(self.repeat)
        self.radioButton.toggled.connect(self.random)
        self.radioButton_3.toggled.connect(self.cycle)
        self.pushButton_4.clicked.connect(self.createpl)
        self.radioButton.setCheckable(False)
        self.radioButton_2.setCheckable(False)
        self.radioButton_3.setCheckable(False)
        self.radioButton_4.setChecked(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.verticalSlider.setValue(int(pg.mixer.music.get_volume() * 100))
        self.verticalSlider.sliderReleased.connect(self.volume)
        self.listWidget_2.itemClicked.connect(self.oneclicklists)
        self.lineEdit.textChanged.connect(self.changeactivetrack)
        self.listWidget_2.setAttribute(Qt.WA_TranslucentBackground)
        self.directchangebtn = QPushButton('Change directory')
        self.directchangebtn.setObjectName('changingdirbtn')
        self.directchangebtn.clicked.connect(self.directchangeact)
        self.updatefilelistbtn = QPushButton('Update')
        self.updatefilelistbtn.setObjectName('updatefilebtn')
        self.updatefilelistbtn.clicked.connect(self.updatefilelistact)
        self.deletinganddownloadingtracks = QPushButton('Download/Delete tracks')
        self.deletinganddownloadingtracks.setObjectName('sysedbtn')
        self.deletinganddownloadingtracks.clicked.connect(deletedownloadact)
        self.stylesheetedtbtn = QPushButton('Set Style')
        self.stylesheetedtbtn.setObjectName('stylesheetedtbtn')
        self.stylesheetedtbtn.clicked.connect(stylesheetedtact)
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addWidget(self.directchangebtn)
        self.toolbar.addWidget(self.updatefilelistbtn)
        self.toolbar.addWidget(self.deletinganddownloadingtracks)
        self.toolbar.addWidget(self.stylesheetedtbtn)
        self.listWidget.installEventFilter(self)
        self.listWidget_2.installEventFilter(self)
        if 'ui_source/main.css' in filespath['main.css']:
            self.pushButton_3.setIcon(QIcon('decor_source/nexttrack.png'))
            self.pushButton_3.setIconSize(QSize(75, 75))
            self.pushButton_2.setIcon(QIcon('decor_source/previoustrack.png'))
            self.pushButton_2.setIconSize(QSize(75, 75))
            self.pushButton.setIcon(QIcon('decor_source/pause.png'))
            self.pushButton.setIconSize(QSize(75, 75))
        self.label_2.setFocus()
        os.chdir(self.workdirect)
        try:
            lines = readfile("playlists.txt", strind=-1)
        except FileNotFoundError:
            with open(filespath["playlists.txt"], mode="w+", encoding="utf-8") as f:
                f.write('')
            lines = readfile("playlists.txt", strind=-1)
        with open(filespath["playlists.txt"], mode="w+", encoding="utf-8") as f:
            lines = [f"'all': {self.allfiles}\n"] + lines[1:]
            f.writelines(lines)
        lines = readfile("playlists.txt", strind=-1)
        createvolume(self.workdirect, self)
        os.chdir(self.workdirect)
        self.lists = [i[:i.find('[') - 2][1:-1] for i in lines]
        self.songslists = [eval('[' + i[i.find('['):][1:-2] + ']') for i in lines]
        [item_render(i, tx, mainobj=self, listwidget=2, editing=True) for i, tx in enumerate(self.lists)]
        [item_render(i, tx, mainobj=self, listwidget=1) for i, tx in enumerate(self.allfiles)]
        self.listfiles = [self.listWidget_2.item(i) for i in range(self.listWidget_2.count())]
        self.files = [self.listWidget.item(i) for i in range(self.listWidget.count())]
        self.filesnme = self.allfiles
        self.quit = QAction("Quit", self)
        self.quit.triggered.connect(self.closeEvent)
        self.addAction(self.quit)

    def keyPressEvent(self, event):
        if event.key() == 16777236 and event.modifiers() == Qt.ControlModifier:
            self.nexttr()
        elif event.key() == 16777234 and event.modifiers() == Qt.ControlModifier:
            self.previous()
        elif event.key() == 16777236:
            self.horizontalSlider.setValue(self.horizontalSlider.value() + 10)
            self.chtme()
        elif event.key() == 16777234:
            self.horizontalSlider.setValue(self.horizontalSlider.value() - 10)
            self.chtme()
        elif event.key() == 16777237:
            self.verticalSlider.setValue(self.verticalSlider.value() - 5)
            self.volume(newvol=self.verticalSlider.value())
        elif event.key() == 16777235:
            self.verticalSlider.setValue(self.verticalSlider.value() + 5)
            self.volume(newvol=self.verticalSlider.value())
        elif event.key() == 16777251:
            self.pause()
        # print(event.key())

    def changeactivetrack(self):
        keyword = self.lineEdit.text().lower()
        track = ''
        for i in self.filesnme:
            if keyword in i.lower():
                track = i
                break
        if track:
            ind = self.filesnme.index(track)
            item = self.files[ind]
            item.setSelected(True)
            # pg.mixer.music.stop()
            # self.activenme = track
            # self.activeitem = item
            self.listWidget.scrollToItem(item, QAbstractItemView.PositionAtTop)

    def directchangeact(self):
        drct = QFileDialog.getExistingDirectory(self, 'Directory', '/home')
        if drct != '' and drct != '/home':
            os.chdir(ex.workdirect)
            clearfile("music_direction.txt")
            with open(filespath["music_direction.txt"], mode="a+", encoding="utf-8") as f:
                f.write(f'music_direct: {drct}\n')
                f.write(f'saving_direct: {ex.workdirect}/mus1_\n')
            ex.direct = drct
            ex.listWidget.clear()
            ex.listWidget_2.clear()
            os.chdir(ex.workdirect)
            ex.allfiles = searchf(ex.direct, ex)
            lines = readfile("playlists.txt", strind=-1)
            with open(filespath["playlists.txt"], mode="w+", encoding="utf-8") as f:
                lines = [f"'all': {ex.allfiles}\n"] + lines[1:]
                f.writelines(lines)
            lines = readfile("playlists.txt", strind=-1)
            createvolume(ex.workdirect, ex)
            os.chdir(ex.workdirect)
            ex.lists = [i[:i.find('[') - 2][1:-1] for i in lines]
            ex.songslists = [eval('[' + i[i.find('['):][1:-2] + ']') for i in lines]
            [item_render(i, tx, mainobj=ex, listwidget=2, editing=True) for i, tx in enumerate(ex.lists)]
            [item_render(i, tx, mainobj=ex, listwidget=1) for i, tx in enumerate(ex.allfiles)]
            ex.listfiles = [ex.listWidget_2.item(i) for i in range(ex.listWidget_2.count())]
            ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]
            ex.filesnme = [i for i in ex.allfiles]
        self.label_2.setFocus()

    def updatefilelistact(self, inr=False):
        if ex.activeplst == 'all' or inr:
            pg.mixer.music.stop()
            ex.filesnme = searchf(ex.direct, ex)
            checkforrepeat(ex)
            ex.allfiles = ex.filesnme
            ex.listWidget.clear()
            ex.activenme = ex.allfiles[0]
            lines = readfile("playlists.txt", strind=-1)
            with open(filespath["playlists.txt"], mode="w+", encoding="utf-8") as f:
                lines = [f"'all': {self.allfiles}\n"] + lines[1:]
                f.writelines(lines)
            createvolume(ex.workdirect, ex)
            lines = readfile("playlists.txt", strind=-1)
            [item_render(i, tx, mainobj=ex, listwidget=1) for i, tx in enumerate(ex.allfiles)]
            ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]
            ex.songslists = [eval('[' + i[i.find('['):][1:-2] + ']') for i in lines]
            ex.listWidget.item(0).setSelected(True)
        self.label_2.setFocus()

    def clickedaddinpl(self):
        pg.mixer.music.stop()
        allp = eval(readfile("playlists.txt", strind=0)[7:])
        ind = int(self.sender().objectName()[7:])
        tracknme = allp[ind]
        lines = readfile("playlists.txt", strind=-1)
        allp = [dlg.listWidget_3.item(i).text() for i in range(dlg.listWidget_3.count())]
        ind = allp.index(tracknme)
        lists = [i[:i.find('[') - 2][1:-1] for i in lines]
        songslists = [eval('[' + i[i.find('['):][1:-2] + ']') for i in lines]
        track = allp[ind]
        playlist = songslists[lists.index(ex.changingpl)]
        if track not in playlist:
            clearfile("playlists.txt")
            os.chdir(ex.workdirect)
            with open(filespath["playlists.txt"], mode="a", encoding="utf-8") as f:
                for i in lines:
                    if ex.changingpl not in i[:i.index(':')]:
                        f.write(i)
                    else:
                        muslist = eval('[' + i[i.find('['):][1:-2] + ']')
                        muslist.append(track)
                        f.write(f"'{ex.changingpl}': {str(muslist)}\n")
            ex.listWidget.clear()
            [item_render(i, tx, mainobj=ex, listwidget=1) for i, tx in enumerate(muslist)]
            ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]
            ex.activenme = muslist[0]
            ex.activeitem = ex.files[0]
            ex.activeitem.setSelected(True)
            ex.label.setText(ex.activenme)
            os.chdir(ex.workdirect)
        dlg.listWidget_3.takeItem(ind)
        item_render(ind, track, md=False, adding=True, mainobj=ex, dlgobj=dlg, listwidget=3, inserting=True)
        ex.filesnme = muslist
        self.label_2.setFocus()

    def clickeddelinpl(self):
        pg.mixer.music.stop()
        ind = int(self.sender().objectName()[7:])
        track = dlg.item_names[ind]
        lines = readfile("playlists.txt", strind=-1)
        clearfile("playlists.txt")
        os.chdir(ex.workdirect)
        with open(filespath["playlists.txt"], mode="a", encoding="utf-8") as f:
            for i in lines:
                if ex.changingpl not in i[:i.index(':')]:
                    f.write(i)
                else:
                    muslist = eval('[' + i[i.find('['):][1:-2] + ']')
                    ind = muslist.index(track)
                    del muslist[ind]
                    f.write(f"'{ex.changingpl}': {str(muslist)}\n")
        ex.listWidget.clear()
        [item_render(i, tx, mainobj=ex, listwidget=1) for i, tx in enumerate(muslist)]
        ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]
        try:
            ex.activenme = muslist[0]
            ex.activeitem = ex.files[0]
            ex.activeitem.setSelected(True)
        except IndexError:
            ex.activenme = None
            ex.activeitem = None
        ex.filesnme = muslist
        ex.label.setText(ex.activenme)
        dlg.listWidget_4.takeItem(ind)
        item_names = [dlg.listWidget_3.item(i).text() for i in range(dlg.listWidget_3.count())]
        ind = item_names.index(track)
        dlg.listWidget_3.takeItem(ind)
        item_render(ind, track, md=True, adding=True, mainobj=ex, dlgobj=dlg, listwidget=3, inserting=True)
        if ex.listWidget.count() == 0:
            ex.label.setText('No Music')
        self.label_2.setFocus()

    def createpl(self):
        name, pressed = QInputDialog.getText(self, 'New Playlist', 'Playlist Name:')
        k = True
        while (name in self.lists or name == '') and (pressed != QInputDialog.Rejected):
            err = QMessageBox.critical(self, 'Incorrect Name', 'Enter another name',
                                       buttons=QMessageBox.Yes | QMessageBox.No)
            if err == QMessageBox.Yes:
                name, pressed = QInputDialog.getText(self, 'New Playlist', 'Playlist Name:')
            else:
                k = False
                break
        if name not in self.lists and k and pressed != QInputDialog.Rejected:
            tdir = os.getcwd()
            os.chdir(ex.workdirect)
            lines = readfile("playlists.txt", strind=-1)
            with open(filespath["playlists.txt"], mode="w", encoding="utf-8") as f:
                lines += [f"'{name}': {[]}\n"]
                f.writelines(lines)
            ex.listWidget_2.clear()
            lines = readfile("playlists.txt", strind=-1)
            lines = [i[:i.find('[') - 2][1:-1] for i in lines]
            [item_render(i, tx, mainobj=ex, listwidget=2, editing=True) for i, tx in enumerate(lines)]
            allp = eval(readfile("playlists.txt", strind=0)[7:])
            lines = readfile("playlists.txt", strind=-1)
            self.activenme = allp[0]
            self.activeplst = 'all'
            self.filesnme = allp
            self.stopedk = 0
            self.listfiles = [ex.listWidget_2.item(i) for i in range(ex.listWidget_2.count())]
            self.lists = [i[:i.find('[') - 2][1:-1] for i in lines]
            self.activeplstitem = ex.listfiles[ex.lists.index('all')]
            os.chdir(tdir)
        self.label_2.setFocus()

    def pause(self):
        if pg.mixer.music.get_busy():
            if 'ui_source/main.css' in filespath['main.css']:
                ex.pushButton.setIcon(QIcon('decor_source/play.png'))
                ex.pushButton.setIconSize(QSize(75, 75))
            ex.stopedk = ex.horizontalSlider.value()
            ex.l = False
            pg.mixer.quit()
            pg.mixer.init(44100, 32, 2, 256)
        else:
            if 'ui_source/main.css' in filespath['main.css']:
                ex.pushButton.setIcon(QIcon('decor_source/pause.png'))
                ex.pushButton.setIconSize(QSize(75, 75))
            if ex.activenme is None:
                try:
                    ex.activenme = ex.filesnme[0]
                    ex.play()
                    ex.l = True
                except IndexError:
                    self.label_2.setFocus()
            else:
                try:
                    ex.play(stt=ex.stopedk)
                    ex.l = True
                except ValueError:
                    pg.mixer.music.stop()
                    self.label_2.setFocus()
        self.label_2.setFocus()

    def next(self, step=1, trackind=-1):
        try:
            tdir = os.getcwd()
            os.chdir(ex.workdirect)
            lines = readfile("playlists.txt", strind=-1)
            for i in lines:
                if ex.activeplst in i[:i.index(':')]:
                    l1 = eval(i[len(ex.activeplst) + 4:-1])
                    ind = l1.index(ex.activenme)
                    try:
                        ex.activenme = l1[ind + step] if trackind == -1 else l1[trackind]
                        ex.activeitem = ex.files[ind + step] if trackind == -1 else ex.files[trackind]
                        ex.activeitem.setSelected(True)
                        ex.listWidget.scrollToItem(ex.activeitem, QAbstractItemView.PositionAtCenter)
                        ex.play()
                    except IndexError:
                        ex.activenme = l1[0]
                        ex.listWidget.scrollToItem(ex.activeitem, QAbstractItemView.PositionAtCenter)
                        ex.play()
                        self.label_2.setFocus()
            os.chdir(tdir)
        except ValueError:
            self.label_2.setFocus()
        self.label_2.setFocus()

    def nexttr(self):
        ex.k = False
        self.label_2.setFocus()
        ex.next()

    def previous(self):
        ex.k = False
        self.label_2.setFocus()
        ex.next(step=-1)

    def repeat(self):
        ex.k = True
        ex.radioButton_2.setChecked(False)
        ex.radioButton_3.setChecked(False)
        ex.update()
        pg.mixer.music.rewind()
        ex.play(stt=ex.horizontalSlider.value())
        ex.update1(newstart=ex.horizontalSlider.value())
        while self.sender().isChecked() and ex.f and ex.k:
            pg.event.get()
            if not pg.mixer.music.get_busy():
                self.label_2.setFocus()
                ex.next(step=0)

    def random(self):
        ex.k = True
        ex.radioButton.setChecked(False)
        ex.radioButton_3.setChecked(False)
        ex.update()
        pg.mixer.music.rewind()
        ex.play(stt=ex.horizontalSlider.value())
        ex.update1(newstart=ex.horizontalSlider.value())
        while self.sender().isChecked() and ex.f:
            pg.event.get()
            if not pg.mixer.music.get_busy():
                self.label_2.setFocus()
                ex.next(trackind=random.randint(0, len(ex.filesnme) - 1))

    def cycle(self):
        ex.k = True
        ex.radioButton.setChecked(False)
        ex.radioButton_2.setChecked(False)
        ex.update()
        pg.mixer.music.rewind()
        ex.play(stt=ex.horizontalSlider.value())
        ex.update1(newstart=ex.horizontalSlider.value())
        while self.sender().isChecked() and ex.f:
            pg.event.get()
            if not pg.mixer.music.get_busy() and ex.l:
                self.label_2.setFocus()
                ex.next()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setWindowTitle('Program Closing')
        close.setText("Are you sure about that?")
        close.setStyleSheet("background-color: #372747; color: white; font: 14px bold")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            event.accept()
            pg.mixer.music.stop()
            ex.f = False
            dlg.closing()
            addanddelldlg.closing()
            ssedact.closing()
            for child in active_children():
                child.terminate()
        else:
            event.ignore()

    def chtme(self):
        self.label_2.setFocus()
        ex.play(stt=ex.horizontalSlider.value())

    def oneclicktracks(self):
        self.label_2.setFocus()
        nme1 = str(
            [self.sender().item(i).text() for i in range(self.sender().count()) if self.sender().item(i).isSelected()])[
               2:-2]
        if pg.mixer.music.get_busy() and nme1 == ex.activenme:
            ex.stopedk = ex.horizontalSlider.value()
            pg.mixer.quit()
            pg.mixer.init(44100, 32, 2, 256)
        elif (not pg.mixer.music.get_busy()) and nme1 == ex.activenme:
            ex.play(stt=ex.stopedk)
        elif nme1 != ex.activenme:
            ex.activenme = nme1
            ex.play()

    def oneclicklists(self):
        self.label_2.setFocus()
        ex.listWidget.clear()
        pg.mixer.music.stop()
        nme1 = str(
            [self.sender().item(i).text() for i in range(self.sender().count()) if self.sender().item(i).isSelected()])[
               2:-2]
        tdir = os.getcwd()
        os.chdir(ex.workdirect)
        lines = readfile("playlists.txt", strind=-1)
        for i in lines:
            if nme1 in i[:i.index(':')]:
                ex.filesnme = eval('[' + i[i.find('['):][1:-2] + ']')
        os.chdir(tdir)
        try:
            ex.activenme = ex.filesnme[0]
        except IndexError:
            ex.activenme = None
            ex.label.setText('No Music')
        ex.activeplstitem = ex.listfiles[ex.lists.index(nme1)]
        ex.activeplst = nme1
        ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]
        try:
            ex.activeitem = ex.files[0]
            ex.activeitem.setSelected(True)
        except IndexError:
            ex.activeitem = None
        ex.activeplstitem.setSelected(True)
        ex.listWidget.clear()
        [item_render(i, tx, mainobj=ex, listwidget=1) for i, tx in enumerate(ex.filesnme)]
        ex.files = [ex.listWidget.item(i) for i in range(ex.listWidget.count())]

    def playlistchanging(self):
        nme1 = int(self.sender().objectName()[7:])
        ex.changingpl = ex.lists[nme1]
        ex.activeplst = ex.lists[nme1]
        if nme1 != 'all':
            changelistdialog(ex.changingpl)

    def volume(self, newvol=False):
        if not newvol:
            pg.mixer.music.set_volume(self.verticalSlider.value() / 100)
        else:
            pg.mixer.music.set_volume(newvol / 100)
        settrackvolume(ex.activenme, pg.mixer.music.get_volume())

    def play(self, stt=0.0):
        tdir = os.getcwd()
        os.chdir(self.workdirect)
        os.chdir(db[ex.activenme])
        ex.time = time()
        try:
            ex.acrmus = pg.mixer.Sound(ex.activenme)
            pg.mixer.music.load(ex.activenme)
            pg.mixer.music.play(start=stt)
        except pg.error:
            ex.label.setText('Sorry, this file format is not supported.')
        try:
            ex.activeitem = self.listWidget.item(self.filesnme.index(ex.activenme))
            ex.activeitem.setSelected(True)
        except IndexError:
            ex.activeitem = None
        ex.horizontalSlider.setMaximum(round(ex.acrmus.get_length()) + 5)
        ex.label.setText(ex.activenme[:-4])
        os.chdir(tdir)
        ex.radioButton.setCheckable(True)
        ex.radioButton_2.setCheckable(True)
        ex.radioButton_3.setCheckable(True)
        os.chdir(ex.workdirect)
        lines = readfile("tracksvolume.txt", strind=-1)
        for i in lines:
            if ex.activenme in i:
                vlme = float(i[i.find(':') + 2:])
                ex.verticalSlider.setValue(int(vlme * 100))
                pg.mixer.music.set_volume(vlme)
        ex.update1(newstart=stt)

    def update1(self, newstart=0.0):
        while pg.mixer.music.get_busy() and ex.f:
            pg.event.get()
            if time() - self.time >= 1:
                ex.time = time()
                ex.horizontalSlider.setValue(int(newstart + pg.mixer.music.get_pos() / 1000))
                ex.update()

    def skipvol(self, vols):
        self.verticalSlider.setValue(self.verticalSlider.value() + vols)
        self.volume(self.verticalSlider.value())

    def skipsec(self, secs):
        self.horizontalSlider.setValue(self.horizontalSlider.value() + secs)
        self.chtme()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def wrap(obj, iconname, colors=['#08465f', '#480644', '#2e3060']):
    obj.setWindowIcon(QIcon(filespath[iconname]))
    p = QPalette()
    gradient = QLinearGradient(QPoint(obj.rect().bottomLeft()), QPoint(obj.rect().topRight()))
    step = 1 / (len(colors) - 1)
    curr = -step
    for i in range(len(colors)):
        gradient.setColorAt(curr + step, QColor(colors[i]))
        curr += step
    p.setBrush(QPalette.Window, QBrush(gradient))
    obj.setPalette(p)


def setfilespathconfig():
    pth = os.getcwd().replace('\\', '/')
    if not os.path.exists(pth + '/config'):
        os.mkdir(pth + '/config')
    if not os.path.exists(pth + '/config/filespath.txt'):
        with open("config/filespath.txt", mode="w+", encoding="utf-8") as f:
            f.write(str(get_filespath()))
    with open("config/filespath.txt", mode="r", encoding="utf-8") as f:
        if f.read() == '':
            with open("config/filespath.txt", mode="w+", encoding="utf-8") as f:
                f.write(str(get_filespath()))


if __name__ == '__main__':
    freeze_support()
    setfilespathconfig()
    with open("config/filespath.txt", mode="r", encoding="utf-8") as f:
        filespath = eval(f.read())
    app = QApplication(sys.argv)
    with open(filespath['main.css'], mode="r") as f:
        app.setStyleSheet(f.read())
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
