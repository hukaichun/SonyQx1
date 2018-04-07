from PyQt4 import QtCore, QtGui

class SliderWidget(QtGui.QWidget):
    def __init__(self, param, parent = None):
        super(SliderWidget,self).__init__(parent)
        self.Manager = {}
        self.initUI(param)
    
    def __getitem__(self, name):
        return self.Manager[name]

    def initUI(self, param):
        text        = QtGui.QLabel(text = param['name']+":")
        sliderValue = QtGui.QLabel()

        self.Manager[param['name']] = QtGui.QSlider(QtCore.Qt.Horizontal)

        self.Manager[param['name']].valueChanged.connect(lambda:sliderValue.setText(str(self.Manager[param['name']].value())))
        self.Manager[param['name']].setMinimum(param['range'][0])
        self.Manager[param['name']].setMaximum(param['range'][1])
        self.Manager[param['name']].setTickInterval(param['range'][2])
        self.Manager[param['name']].setTickPosition(QtGui.QSlider.TicksBelow)
        self.Manager[param['name']].setValue(param['default'])
        text.setAlignment(QtCore.Qt.AlignRight)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(text)
        hbox.addWidget(self.Manager[param['name']])
        hbox.addWidget(sliderValue)
        self.setLayout(hbox)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    param = {
        "name"   : "sliderBar",
        "range"  : (0, 100, 1),
        "default": 50
    }
    demo = SliderWidget(param)
    demo.show()
    sys.exit(app.exec_())
        
