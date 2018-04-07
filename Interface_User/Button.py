from PyQt4 import QtGui

class ButtonWidget(QtGui.QWidget):
    def __init__(self, functionList, parent = None, direction = "V" ):
        super(ButtonWidget,self).__init__(parent)
        self.Manager = {}
        self.direct = direction
        self.initUI(functionList)

    def initUI(self, functionList):
        if self.direct == "V":
            box = QtGui.QVBoxLayout()
        elif self.direct == "H":
            box = QtGui.QHBoxLayout()

        for name in functionList:
            self.Manager[name] = QtGui.QPushButton(self, text = name)
            box.addWidget(self.Manager[name])
        self.setLayout(box)

    def __getitem__(self, name):
        return self.Manager[name]

        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    funlist = ['b1','b2','b3','b4','b5','b6','b7','b8']
    demo = ButtonWidget(funlist, direction = "H")
    print demo['b1']
    demo.show()
    sys.exit(app.exec_())
