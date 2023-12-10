#!/usr/bin/env python3

import sys, json
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets



class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        str = """
        {"time":[0.000000,0.000050,0.000100,0.000150,0.000200,0.000250,0.000300,0.000350,0.000400,0.000450,0.000500,0.000550,0.000600,0.000650,0.000700,0.000750,0.000800,0.000850,0.000900,0.000950,0.001000,0.001050,0.001100,0.001150,0.001200,0.001250,0.001300,0.001350,0.001400,0.001450,0.001500,0.001550,0.001600,0.001650,0.001700,0.001750,0.001800,0.001850,0.001900,0.001950,0.002000,0.002050,0.002100,0.002150,0.002200,0.002250,0.002300,0.002350,0.002400,0.002450,0.002500,0.002550,0.002600,0.002650,0.002700,0.002750,0.002800,0.002850,0.002900,0.002950,0.003000,0.003050,0.003100,0.003150,0.003200,0.003250,0.003300,0.003350,0.003400,0.003450,0.003500,0.003550,0.003600,0.003650,0.003700,0.003750,0.003800,0.003850,0.003900,0.003950,0.004000,0.004050,0.004100,0.004150,0.004200,0.004250,0.004300,0.004350,0.004400,0.004450,0.004500,0.004550,0.004600,0.004650,0.004700,0.004750,0.004800,0.004850,0.004900,0.004950],"Vbus.V.y1":[31.85,31.89,31.81,31.85,31.85,31.93,31.89,31.89,31.89,31.81,31.81,31.81,31.81,31.81,31.81,31.78,31.81,31.81,31.81,31.89,31.89,31.85,31.89,31.89,31.93,31.93,31.89,31.96,31.93,31.89,31.93,32.00,31.89,31.89,31.85,31.89,31.89,31.85,31.96,31.85,31.81,31.81,31.89,31.89,31.93,31.89,31.85,31.85,31.81,31.78,31.78,31.85,31.81,31.81,31.81,31.85,31.70,31.81,31.81,31.81,31.78,31.85,32.07,31.78,31.85,31.81,31.85,31.85,31.85,31.85,31.89,31.85,31.85,31.85,31.70,32.19,31.85,31.78,31.81,31.81,31.78,31.25,31.85,31.81,31.78,31.81,31.81,31.81,31.85,31.89,31.89,31.93,31.93,31.93,31.93,31.89,31.96,31.89,31.93,31.89],"Iu.I_phase.y1":[1.40,1.40,0.93,0.70,0.47,2.79,4.19,4.65,4.65,3.26,2.33,2.33,2.33,1.63,1.16,0.47,-0.00,0.23,0.47,1.16,0.93,1.63,0.93,-0.70,-0.47,-0.00,0.47,0.93,1.16,-0.00,-1.40,-2.09,-2.56,-3.02,-2.79,-2.33,-2.09,-2.33,-2.33,-2.33,-2.33,-1.16,0.93,2.56,3.26,3.72,2.79,1.63,1.86,2.79,2.79,2.56,2.33,1.16,0.70,1.40,2.33,2.56,3.72,2.79,0.70,-1.40,-1.86,-2.09,-1.63,-0.70,-0.23,-0.70,-0.93,-0.93,-1.40,-1.86,-0.93,-0.00,-0.47,-0.23,-0.93,-2.56,-3.26,-3.02,-1.86,-1.40,-2.33,-3.72,-3.49,-1.63,-1.16,-0.23,-0.93,-0.47,-1.16,-1.40,-1.40,-0.93,-1.16,-0.93,-0.93,-1.16,-2.09,-2.09],"Iv.I_phase.y1":[-2.09,-2.79,-2.56,-2.33,-2.56,-3.26,-4.42,-4.88,-4.88,-4.65,-3.26,-2.33,-2.56,-2.79,-3.72,-5.35,-5.35,-3.49,-2.33,-2.09,-2.56,-3.02,-3.02,-1.63,-0.70,0.23,-0.23,0.23,-0.23,-0.23,-0.93,-0.47,0.23,0.93,2.09,1.16,1.16,0.93,0.70,-0.00,-0.23,-0.70,-1.16,-2.33,-3.02,-3.02,-3.26,-2.09,-1.16,-0.70,-0.00,-0.47,-0.70,-1.63,-2.33,-2.33,-2.09,-3.26,-3.02,-2.79,-0.23,0.70,2.56,2.56,1.40,0.23,-0.93,-0.47,-0.23,-0.70,-1.40,-1.86,-1.63,-3.49,-4.88,-5.58,-4.42,-2.09,-0.23,-0.23,-1.16,-2.09,-1.86,-1.63,-1.16,-0.23,-0.93,-0.23,-1.16,-1.63,-2.56,-1.63,-0.47,0.47,0.70,1.63,2.09,1.86,2.09,2.56],"Iw.I_phase.y1":[0.93,1.16,1.86,1.63,0.47,-0.00,-0.70,-1.40,-0.93,-0.47,-0.47,-1.86,-2.56,-1.40,0.93,2.79,3.26,1.63,-0.47,-0.23,-0.23,-0.00,-0.00,0.47,-0.47,-0.70,-0.93,-1.86,-1.86,-0.47,0.47,0.93,1.16,0.70,-0.93,-0.23,0.70,1.63,2.33,2.79,3.26,0.93,-0.23,-0.93,-1.40,-0.93,-0.93,-0.93,-3.49,-5.12,-5.58,-5.35,-3.72,-1.40,-0.23,-0.93,-1.16,-1.16,-1.86,-2.09,-1.40,-1.40,-0.93,-0.47,-0.00,-0.47,-0.23,-0.00,-0.00,0.93,1.86,2.33,2.79,4.65,5.58,5.81,5.58,4.65,3.49,2.79,2.79,2.79,3.49,4.88,4.19,2.09,-0.70,-0.93,-0.93,-0.00,1.63,1.86,0.47,-0.93,-1.63,-2.79,-3.26,-2.79,-2.09,-2.33],"Vd.V_dq.y1":[1.46,1.51,1.47,1.44,1.40,1.55,1.64,1.64,1.60,1.43,1.50,1.56,1.57,1.44,1.23,1.02,0.96,1.09,1.16,1.15,1.09,1.04,1.22,1.35,1.34,1.29,1.25,1.17,1.15,1.25,1.32,1.34,1.32,1.23,1.20,1.23,1.20,1.18,1.17,1.18,1.15,1.20,1.33,1.45,1.48,1.50,1.38,1.43,1.61,1.71,1.71,1.64,1.51,1.33,1.22,1.18,1.16,1.02,0.98,1.13,1.27,1.42,1.43,1.43,1.40,1.32,1.31,1.33,1.32,1.38,1.44,1.45,1.50,1.64,1.73,1.75,1.61,1.38,1.22,1.19,1.24,1.23,1.11,0.95,1.00,1.14,1.37,1.38,1.34,1.25,1.12,1.16,1.26,1.33,1.32,1.34,1.51,1.48,1.51,1.47],"Vq.V_dq.y1":[16.17,16.10,16.05,16.03,15.98,16.01,15.92,15.84,15.79,15.78,15.84,15.85,15.76,15.78,15.86,15.91,16.02,16.05,15.97,16.03,16.06,16.12,16.15,16.16,16.09,16.09,16.11,16.09,16.13,16.15,16.08,16.03,15.99,15.94,15.97,16.00,16.03,16.02,16.02,15.99,15.99,16.04,16.12,16.07,16.00,15.97,15.92,15.98,15.95,15.86,15.83,15.74,15.79,15.90,15.97,15.94,15.96,15.97,15.97,15.99,16.03,15.95,15.95,15.95,16.01,16.04,16.10,16.08,16.06,16.09,16.06,16.00,16.04,16.03,15.88,15.79,15.75,15.77,15.88,15.93,15.93,15.89,15.91,15.97,16.07,16.16,16.02,16.06,15.98,16.01,16.09,16.21,16.18,16.10,16.05,15.96,15.89,15.89,15.89,15.84],"angle.misc.y1":[23490,25254,27021,28787,30537,32316,34058,35782,37498,39212,40952,42674,44346,46049,47761,49502,51271,53025,54731,56501,58262,60050,61830,63620,65377,1622,3406,5171,6965,8751,10511,12270,14029,15783,17562,19343,21125,22886,24658,26416,28184,29982,31802,33576,35329,37085,38819,40594,42330,44033,45743,47384,49136,50929,52712,54451,56212,57972,59736,61510,63304,65056,1294,3065,4850,6627,8418,10184,11946,13730,15493,17244,19024,20781,22464,24158,25845,27544,29277,30984,32700,34426,36174,37936,39725,41528,43252,45042,46782,48565,50373,52206,53985,55743,57505,59247,60985,62745,64496,694]}
        """

        self.streamDict = json.loads(str)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = MatplotlibCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas)

        self.button = QPushButton("Update Plot", self)
        self.button.clicked.connect(self.canvas.update_plot)
        self.layout.addWidget(self.button)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(width, height), dpi=dpi)

        self.axes = [ax1, ax2, ax3, ax4]

        self.streamDict = parent.streamDict

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_plot(self):
        for ax in self.axes:
            ax.clear()

        # 'time',
        x = np.array(self.streamDict['time'])

        # 'Vbus.V.y1',
        y1_1 = np.array(self.streamDict['Vbus.V.y1'])

        # 'Iu.I_phase.y1', 'Iv.I_phase.y1', 'Iw.I_phase.y1',
        y2_1 = np.array(self.streamDict['Iu.I_phase.y1'])
        y2_2 = np.array(self.streamDict['Iv.I_phase.y1'])
        y2_3 = np.array(self.streamDict['Iw.I_phase.y1'])

        # 'Vd.V_dq.y1', 'Vq.V_dq.y1'
        y3_1 = np.array(self.streamDict['Vd.V_dq.y1'])
        y3_2 = np.array(self.streamDict['Vq.V_dq.y1'])

        # 'angle.misc.y1'
        y4_1 = np.array(self.streamDict['angle.misc.y1'])

        self.axes[0].plot(x, y1_1, label='Vbus')
        self.axes[0].set_title('Vbus')
        self.axes[0].set_ylim(0, np.max(y1_1) + int(np.max(y1_1) * .2))

        y = np.concatenate((y2_1, y2_2, y2_3), axis=None)
        min = np.min(y) 
        max = np.max(y)
        min = min - (abs(min) * .2)
        max = max + (max * .2)
        self.axes[1].plot(x, y2_1, label='Iu')
        self.axes[1].plot(x, y2_2, label='Iv')
        self.axes[1].plot(x, y2_3, label='Iw')
        self.axes[1].set_ylim(min, max)
        self.axes[1].set_title('I')
        self.axes[1].legend(loc='upper right')

        y = np.concatenate((y3_1, y3_2), axis=None)
        min = np.min(y) 
        max = np.max(y)
        min = min - (abs(min) * .2)
        max = max + (max * .2)
        self.axes[2].plot(x, y3_1, label='Vd')
        self.axes[2].plot(x, y3_2, label='Vq')
        self.axes[2].set_ylim(0, max)
        self.axes[2].set_title('Vd/Vq')
        self.axes[2].legend(loc='upper right')

        self.axes[3].plot(x, y4_1, label='angle')
        self.axes[3].set_title('Angle')
        self.axes[3].legend(loc='upper right')

        for ax in self.axes:
            ax.grid()

        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MyMainWindow()
    mainWin.show()
    sys.exit(app.exec_())
