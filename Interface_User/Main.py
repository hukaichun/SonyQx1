import Button
import Tab
import Image
import Combo
import Slider
from PyQt4 import QtGui, QtCore

class MainWidget(QtGui.QWidget):
    tabList    = {'Scan'              : ['Update Camera Info', 'Live view', 'Focus', 
                                         'actShutter', 'Scan'],
                  'Pattern Check'     : ['Structed Light Mode', 'Calibration Mode', 
                                         'Next Pattern', 'Full/Sub Screen'], 
                  'file'              : ['Small Size', 'Large Size','Original Size', 
                                         'Delete ALL', 'Upload To Server'],
                  'Truntable'         : ['Direction', 'Rotate', 'Rotate until']}
    
    setting1   = {'Still Quality'     : ['RAW+JPEG', 'Fine', 'Standard'],
                  'Exposur Mode'      : ['Intelligent Auto', 'Superior Auto', 'Program Auto',
                                         'Aperture', 'Shutter'],
                  'Still Size'        : ["3:2,20M", "3:2,10M", "3:2,5.0M",
                                         "16:9,17M", "6:9,8.4M", "16:9,4.2M"]}

    setting2   = {'Iso Speed'         : ['AUTO', '100', '125', '160', '200', '250', '320', '400', 
                                         '500', '640', '800', '1000', '1250', '1600', '2000', '2500',
                                         '3200', '4000', '5000', '6400', '8000', '10000', '12800',
                                         '16000'],
                  'Shutter Speed'     : ['30"', '25"', '20"', '15"', '13"', '10"', '8"', '6"', '5"',
                                         '4"', '3.2"', '2.5"', '2"', '1.6"', '1.3"', '1"', '0.8"',
                                         '0.6"', '0.5"', '0.4"', '1/3', '1/4', '1/5', '1/6', '1/8',
                                         '1/10', '1/13', '1/15', '1/20', '1/25', '1/30', '1/40', 
                                         '1/50', '1/60', '1/80', '1/100', '1/125', '1/160', '1/200',
                                         '1/250', '1/320', '1/400', '1/500', '1/640', '1/800', 
                                         '1/1000', '1/1250', '1/1600', '1/2000', '1/2500', '1/3200',
                                         '1/4000'],
                  'fNumber'           : ['1.8', '2.0', '2.2', '2.5', '2.8', '3.2', '3.5', '4.0', 
                                         '4.5', '5.0', '5.6', '6.3', '7.1', '8.0', '9.0', '10', 
                                         '11', '13', '14', '16', '18', '20', '22']}

    setting3   = {'Cont Shooting Mode': ['Single', 'Continuous', 'Spd Priority Cont.'],
                  'Beep Mode'         : ['On', 'Off'],
                  'White Balance'     : [str((i+25)*100) if i!=75 else 'Auto WB' for i in range(76)]}

    innerDelay = {'name'              : "Between Pattern",
                  'range'             : (0, 100, 10),
                  'default'           : 30}    
    
    beginDelay = {'name'              : "Before Shutter",
                  'range'             : (0, 100, 10),
                  'default'           : 50}    

    rotateAng  = {'name'              : "Rotate Angle",
                  'range'             : (0, 180, 45),
                  'default'           : 40}

    def __init__(self, parent = None):
        super(MainWidget, self).__init__(parent)
        self.Manager     = {}
        self.initUI()

    def __getitem__(self, name):
        return self.Manager[name]

    def initUI(self):
        self.innerDelayValue         = QtGui.QLabel()
        self.Manager[         'Tab'] = Tab.TabWidget(parent = self, tabList = MainWidget.tabList)
        self.Manager[    'Liveview'] = Image.ImageDisplay(self)
        self.Manager[   'Projector'] = Image.ProjectorWidget()
        self.Manager[    'Setting1'] = Combo.ComboBoxWidget(   parent = self, 
                                                            comboList = MainWidget.setting1)
        self.Manager[    'Setting2'] = Combo.ComboBoxWidget(   parent = self, 
                                                            comboList = MainWidget.setting2)
        self.Manager[    'Setting3'] = Combo.ComboBoxWidget(   parent = self,
                                                            comboList = MainWidget.setting3)
        self.Manager[ 'Inner Delay'] = Slider.SliderWidget(parent = self,
                                                           param  = MainWidget.innerDelay)        
        self.Manager[ 'Begin Delay'] = Slider.SliderWidget(parent = self,
                                                           param  = MainWidget.beginDelay)
        self.Manager['Rotate Angle'] = Slider.SliderWidget(parent = self,
                                                           param  = MainWidget.rotateAng)
       
        self.Manager[      'Tab'].setFixedSize(250,480)
        self.Manager[ 'Liveview'].setMinimumSize(960,480)
        self.Manager[ 'Liveview'].setAlignment(QtCore.Qt.AlignCenter)
        
        vbox   = QtGui.QVBoxLayout()
        hbox   = QtGui.QHBoxLayout()
        sbox   = QtGui.QHBoxLayout()
        layout = QtGui.QFormLayout()
        
        sbox.addWidget(self.Manager[ 'Inner Delay'])
        sbox.addWidget(self.Manager[ 'Begin Delay'])
        sbox.addWidget(self.Manager['Rotate Angle'])
        vbox.addWidget(self.Manager[    'Liveview'])
        vbox.addLayout(sbox)
        hbox.addLayout(vbox)
        hbox.addWidget(self.Manager['Tab'])
        layout.addRow(hbox)
        layout.addRow(self.Manager['Setting1'])
        layout.addRow(self.Manager['Setting2'])
        layout.addRow(self.Manager['Setting3'])
        self.setLayout(layout)
        self.Manager['Projector'].setWindowTitle('Structed Light')


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWidget()
    win.show()
    win['Projector'].show()
   # win['Projector'].setWindowFlags(QtCore.Qt.Dialog)

    sys.exit(app.exec_())

