#!/usr/bin/env python3

import sys, json
import datetime
import time
import math
import colorsys

from configparser import ConfigParser
import Payload, speedoPort, speedoPrefs
from keySound import keySound

import speedoObjects
import speedoThermo
import ColorSegmentRing

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsItemGroup
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtGui import QPolygonF, QLinearGradient, QBrush

import qdarkgraystyle

class speedo(QtWidgets.QMainWindow):
    def __init__(self):
        super(speedo, self).__init__()

        self.installEventFilter(self)

        self.max_amps = 200

        ### Config file controls tab variables ### 
        file_path = "app_specs.json"
        try:
            with open(file_path, 'r') as json_file:
                try:
                    t = json.load(json_file)
                    self.tab_data = t['tab_data']
                    self.presets = t['presets']
                except json.JSONDecodeError as json_error:
                    print(f"Error decoding JSON: {json_error}")
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
            
        ### Config file controls UI variables ### 
        config = ConfigParser()
        try:
            with open('app_specs.ini', 'r') as configfile:
                config.read_file(configfile)
        except FileNotFoundError:
            print("Config file not found")

        self.useKeypresses = [False]


        if config.get('Settings', 'use_keypresses') == 'True':
            self.useKeypresses = [True]
        if config.get('Settings', 'use_keypress_sound') == 'True':
            self.keyPressSound = [True]

        self.sound = keySound()

        self.port_substring = config.get('Settings', 'port_substring')
        self.module_directory = config.get('Settings', 'module_directory')

        self.min_width = 1920
        self.min_height = 1080

        ### Window ### 
        self.setMinimumWidth(self.min_width)
        self.setMinimumHeight(self.min_height)

        self.updateTabs = []
        self.tabWidget = QtWidgets.QTabWidget()
        self.statusText = QtWidgets.QLabel(self)

        # payload stuff
        self.serialPayload = Payload.Payload()
        self.serialPayload.startTimer()

        ### create display tab here ###
        self.speedoTab = SpeedoTab(self)
        self.tabWidget.addTab(self.speedoTab, "speedo")
        self.updateTabs.append(self.speedoTab)

        ### tab to open serial
        self.port_tab = speedoPort.Port(self)
        self.tabWidget.addTab(self.port_tab,'Port')
        self.updateTabs.append(self.port_tab)

        ### tab for preferences
        self.prefsTab = speedoPrefs.speedoPrefs(self)
        self.tabWidget.addTab(self.prefsTab,"Prefs")
        self.updateTabs.append(self.prefsTab)

        self.setWindowTitle("speedo")
        self.setCentralWidget(self.tabWidget)

        self.tabWidget.currentChanged.connect(self.tab_changed)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_G:
            self.sound.key_sound(self.keyPressSound[0])
            print("MAIN: get")
        elif key == Qt.Key_O:
            self.sound.key_sound(self.keyPressSound[0])
            print("MAIN: open")
        elif key == Qt.Key_D:
            print("MAIN: switch forward")
            self.sound.key_sound(self.keyPressSound[0])
            current_tab_index = self.tabWidget.currentIndex()
            next_tab_index = (current_tab_index + 1) % self.tabWidget.count()
            self.tabWidget.setCurrentIndex(next_tab_index)
        elif key == Qt.Key_A:
            print("MAIN: switch back")
            self.sound.key_sound(self.keyPressSound[0])
            current_tab_index = self.tabWidget.currentIndex()
            next_tab_index = (current_tab_index - 1) % self.tabWidget.count()
            self.tabWidget.setCurrentIndex(next_tab_index)
        else:
            super().keyPressEvent(event)

    # things to do when a new serial-json string comes in.
    #  this could feeds json to the other tabs 
    #  and sends to the speedo display
    def updateJsonData(self, str):
        str = str.rstrip('\n')
        for row in str.split('\n'):
            try:
                self.streamDict = json.loads(row)
                # there's different types of json that come down the pipe
                if self.streamDict.get('time'):
                    pass
                if self.streamDict.get('vbus'):
                    for tab in self.updateTabs:
                        if hasattr(tab, 'updateValuesWithStream'):
                            tab.updateValuesWithStream(self.streamDict)
                    pass
                    # self.statusBar.updateStatusJson(self.streamDict)
            except json.JSONDecodeError as e:
                print("Getting bad json: {0}".format(row))

    # things to do when NON json data comes in
    #  if any tabs show data, update those tabs
    #  ignored for now, but could change display settings
    def updateTabsWithGet(self):
        if len(self.serialPayload.reportString()) > 0:
            self.serialPayload.parsePayload()
            p = self.serialPayload.reportPayload()
            # print("names: {0}".format(p['names']))
            # update tabs if the payload has anything, 
            if p is not None and len(p['names']) > 0:
                for tab in self.updateTabs:
                    if hasattr(tab, 'updateValuesWithGet'):
                        tab.updateValuesWithGet(p)

    def tab_changed(self, index):
        self.sound.key_sound(self.keyPressSound[0])

### Creates a tab that is described in a json config file
class SpeedoTab(QtWidgets.QWidget):  # Use QWidget instead of QMainWindow
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.min_width = parent.min_width
        self.min_height = parent.min_height
        self.statusText = self.parent.statusText
        self.mid_x = self.min_width / 2
        self.mid_y = self.min_height / 2
        self.max_amps = parent.max_amps

        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        self.graphics_view = QGraphicsView(self)
        scene = QGraphicsScene(self)
        bck = QGraphicsPolygonItem(QPolygonF([QPointF(0, 0), QPointF(self.min_width, 0),
                                              QPointF(self.min_width, self.min_height),
                                              QPointF(0, self.min_height), QPointF(0, 0)]))
        bck.setBrush(QColor(Qt.black))
        scene.addItem(bck)

        (self.ampObjs, self.ampNums) = self.createAmpScale(scene,
                                                           speedoObjects.SpeedoData().ampRect,
                                                           speedoObjects.SpeedoData().ampCaption,
                                                           speedoObjects.SpeedoData().ampNum)


        self.log_button = LogButton(speedoObjects.SpeedoData().logButton, "LOG")
        scene.addItem(self.log_button)

        self.gradientThing(scene)
        self.speedText = self.setSpeedText(scene, speedoObjects.SpeedoData().mphDigit)
        self.timeText = self.setTimeText(scene, speedoObjects.SpeedoData().time)

        self.updateAmpMeter(12, self.ampObjs, self.ampNums)

        self.graphics_view.setScene(scene)
        main_layout.addWidget(self.graphics_view)
        self.setWindowTitle('Polygon Coloring App with QLCDNumber')

        self.thermo1 = speedoThermo.SpeedoThermo(1000, 900, 120, 40, 25, 90, True, "motor")
        scene.addWidget(self.thermo1)

        self.thermo2 = speedoThermo.SpeedoThermo(1400, 900, 120, 40, 25, 90, False, "mosfets")
        scene.addWidget(self.thermo2)

        # helpful timer to update display
        self.streaming_reset = 0
        self.timer = QTimer(self) 
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start(200)

    def updateDisplay(self): 
        current_time = datetime.datetime.now()
        hour = current_time.hour
        minute = current_time.minute

        self.thermo1.setThermoTemp(32)
        self.thermo2.setThermoTemp(60)

        if hour > 12:
            self.timeText.setPlainText("{}:{:02d}".format(hour-12, minute))
        else:
            self.timeText.setPlainText("{}:{:02d}".format(hour, minute))

        if self.streaming_reset > 3: # let it go by a couple ticks before changing
            self.log_button.setText("LOG")
            self.log_button.setColor(QColor(Qt.red))

        self.streaming_reset += 1

    def setTimeText(self, scene, digit):
        (x_min, y_min, x_max, y_max) = self.boundingBox(digit[0])
        return(self.placeFlushLeft(scene, x_min, y_min, "time", (y_max - y_min)))

    def setSpeedText(self, scene, digit):
        (x_min, y_min, x_max, y_max) = self.boundingBox(digit[0])
        return(self.placeFlushRight(scene, 1470, 384, "XXX", (y_max - y_min)))
        
    def placeFlushLeft(self, scene, x, y, str, font_size):
        text = QtWidgets.QGraphicsTextItem(str)
        _font = QtGui.QFont("Futura", font_size, QtGui.QFont.Medium, italic=True)
        _font.setBold(False)

        text.setFont(_font)
        text.setPlainText(str)
        text.setDefaultTextColor(QColor(Qt.white))

        fm = QtGui.QFontMetricsF(_font)
        box = fm.tightBoundingRect(text.toPlainText())
        text.setPos(x - box.left(), -(fm.ascent() + box.top()) + y)
        text.setPos(x, -(fm.ascent() + box.top()) + y)
        scene.addItem(text)
        return(text)

    def placeFlushRight(self, scene, x, y, str, font_size):
        text = QtWidgets.QGraphicsTextItem(str)
        _font = QtGui.QFont("Futura", font_size, QtGui.QFont.Medium, italic=True)
        _font.setBold(False)

        text.setFont(_font)
        text.setPlainText(str)
        text.setDefaultTextColor(QColor(Qt.white))

        fm = QtGui.QFontMetricsF(_font)
        box = fm.tightBoundingRect(text.toPlainText())
        text.setPos(x - box.right(), -(fm.ascent() + box.top()) + y)
        scene.addItem(text)
        return(text)

    def updateFlushRight(self, text_item, x, y, str):
        text_item.setPlainText(str)
        fm = QtGui.QFontMetricsF(text_item.font())
        box = fm.tightBoundingRect(text_item.toPlainText())
        text_item.setPos(x - box.right(), -(fm.ascent() + box.top()) + y)

    def createAmpScale(self, scene, ampRects, caption, ampNums):
        (x_min, y_min, x_max, y_max) = self.boundingBox(caption[0])

        # place static caption
        c = QGraphicsTextItem("Amps")
        font = QFont("Futura", 60, QFont.Medium, italic=True)
        c.setFont(font)
        c.setDefaultTextColor(QColor(Qt.white))
        c.setPos(x_min, y_min)
        scene.addItem(c)

        # place polygons that form the scale
        ampObjs = []
        for array in ampRects:
            l = []
            for (x,y) in array:
                l.append(QPointF(x, y))
                item = QPolygonF(l)
            item = QGraphicsPolygonItem(item)
            item.setBrush(QColor(Qt.white))
            scene.addItem(item)
            ampObjs.append(item)

        # place polygons that form the scale
        h = 0
        for array in ampNums:
            (x_min, y_min, x_max, y_max) = self.boundingBox(array)
            h = max(h, y_max - y_min)

        font_size = self.attemptFontSize(h)
        ampNumObjs = []
        a = 0
        amp_increment = int(self.max_amps / 5)

        for array in ampNums:
            (x_min, y_min, x_max, y_max) = self.boundingBox(array)
            t = QGraphicsTextItem(str(a))
            font = QFont("Futura", font_size, QFont.Medium, italic=True)
            t.setFont(font)
            t.setDefaultTextColor(QColor(Qt.white))

            x = t.boundingRect().center().x()
            y = t.boundingRect().center().y()

            t.setPos(x_max - x, y_min - (h/2))

            scene.addItem(t)

            ampNumObjs.append(t)
            a += amp_increment

        return(ampObjs, ampNumObjs)

    def updateAmpMeter(self, amps, objs, nums):
        length = len(objs) - 1

        if amps < 0: amps = 0
        if amps > self.max_amps: amps = self.max_amps

        amp_increment = int(self.max_amps / 5)

        for i, t in enumerate(nums):
            if amps >= i * amp_increment:
                t.setDefaultTextColor(QColor(Qt.red))
            else:
                t.setDefaultTextColor(QColor(Qt.white))

        pos = int((amps / self.max_amps) * length) + 1
        for i, t in enumerate(objs):
            if i <= pos:
                objs[i].setBrush(QColor(Qt.red))
            else:
                objs[i].setBrush(QColor(Qt.white))

    def updateAmpValues(self):
        print(self.max_amps)
        amp_increment = int(self.max_amps / 5)
        a = 0
        for i, t in enumerate(self.ampNums):
            self.ampNums[i].setPlainText("{}".format(a))
            a += amp_increment

    def gradientThing(self, scene):
        polygon = QPolygonF([QPointF(300, 0), QPointF(400, 0), QPointF(350, 100)])

        # Create a QGraphicsPolygonItem
        item = QGraphicsPolygonItem(polygon)
        gradient = QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0, QColor(255, 0, 0))  # Starting color
        gradient.setColorAt(1, QColor(0, 0, 0, 0)) 

        item.setFlag(item.ItemIsSelectable, True)  # Enable selection
        item.setFlag(item.ItemIsFocusable, True)  # Enable focus

        # Set the brush with the gradient
        brush = QBrush(gradient)
        item.setBrush(brush)
        scene.addItem(item)

    def boundingBox(self, array):
        x_min = array[0][0]
        y_min = array[0][1]
        x_max = array[0][0]
        y_max = array[0][1]
        for pts in array:
            x_min = min(x_min, pts[0])
            y_min = min(y_min, pts[1])
            x_max = max(x_max, pts[0])
            y_max = max(y_max, pts[1])

        return([x_min, y_min, x_max, y_max])

    def attemptFontSize(self, f):
        return(int(f * 1.3))

    def updateValuesWithGet(self, struct):
        if 'curr_max' in struct:
            print(struct['curr_max'])
            self.max_amps = int(float(struct['curr_max']['value']))
            self.updateAmpValues()

    def updateValuesWithStream(self, struct):
        s = str(int(struct['ehz']))
        for i in range(3):
            if len(s) > 2:
                break
            s = ' ' + s
        self.updateFlushRight(self.speedText, 1470, 384, s)

        self.streaming_reset = 0

        html_color = self.buttonColorGenerator(frequency=.4, amplitude=0.5, phase_shift=0, hue = 0.33) 
        self.log_button.setColor(QColor(html_color))
        self.log_button.setText("REC")

    # throbs colors based on math!
    def buttonColorGenerator(self, frequency, amplitude, phase_shift, hue):
        current_time = time.time()
        angle = (2 * math.pi * frequency * current_time) + phase_shift
        value = (math.sin(angle) + 1) / 2
        value *= amplitude
        saturation = 1.0
        lightness = (1 - value) - .2
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        html_color = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))
        return html_color

class LogButton(QGraphicsItemGroup):
    def __init__(self, array, str, parent=None):
        super().__init__(parent)
        
        l = []
        for (x,y) in array[0]:
            l.append(QPointF(x, y)) 
        self.polygon_item = QGraphicsPolygonItem(QPolygonF(l))
        self.polygon_item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.polygon_item.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.addToGroup(self.polygon_item)
        
        self.bb = self.polygon_item.boundingRect()

        font_size = int(self.bb.height() / 2)
        self.text_item = QtWidgets.QGraphicsTextItem(str)
        font = QtGui.QFont("Futura", font_size, QtGui.QFont.Medium, italic=True)
        font.setBold(True)

        self.text_item.setFont(font)
        self.text_item.setPlainText(str)
        self.text_item.setDefaultTextColor(QColor(Qt.white))
        self.addToGroup(self.text_item)

        self.setColor(QColor(Qt.red)) 
        self.setText(str)

    def setColor(self, color):
        self.polygon_item.setBrush(color)
        
    def setText(self, str):
        x = self.bb.topLeft().x()
        y = self.bb.topLeft().y()
        w = self.bb.width()
        h = self.bb.height()
        self.text_item.setPlainText(str)
        fm = QtGui.QFontMetricsF(self.text_item.font())
        box = fm.tightBoundingRect(self.text_item.toPlainText())
        self.text_item.setPos(x + (w/2) - ((box.right() - box.left()) / 2), y + (h/2) + box.top())

    def get_button(self):
        return(self.polygon_item, self.text_item)
    
    def mousePressEvent(self, event):
        if self.text_item.isUnderMouse() or self.polygon_item.isUnderMouse():
            print("Grouped Item Clicked!")
        else:
            super().mousePressEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkgraystyle.load_stylesheet())
    window = speedo()
    window.show()
    app.exec()

