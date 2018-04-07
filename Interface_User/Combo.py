from PyQt4 import QtGui, QtCore

class ComboBoxWidget(QtGui.QWidget):
    def __init__(self, comboList,parent = None):
        super(ComboBoxWidget, self).__init__(parent)
        self.Manager = {}
        self.initUI(comboList)

    def __getitem__(self, name):
        return self.Manager[name]
    
    def initUI(self, args):
        layout = QtGui.QHBoxLayout()
        for item in args:
            self.Manager[item] = QtGui.QComboBox(self)
            for text in args[item]: 
                self.Manager[item].addItem(text)
            _ = QtGui.QLabel(text = item + ":")
            _.setAlignment(QtCore.Qt.AlignRight)
            layout.addWidget(_)
            layout.addWidget(self.Manager[item])

        self.setLayout(layout)

if __name__ == "__main__":
    import sys

    def printt(args):
        print args

    app = QtGui.QApplication(sys.argv)
    lists = {
        "ISO"        : ['AUTO', '100', '125', '160', '200'],
        "Shutter"    : ['1/3','1/4', '1/5']
    }
    demo = ComboBoxWidget(lists)
    demo['ISO'].currentIndexChanged.connect(lambda i: printt("Current index "+str(i)+ ' ISO'))
    demo['Shutter'].currentIndexChanged.connect(lambda i: printt("Current index "+str(i)+ ' Shutter'))
    demo.show()
    sys.exit(app.exec_())


