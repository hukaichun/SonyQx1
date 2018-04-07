import Button
from PyQt4 import QtGui

class TabWidget(QtGui.QTabWidget):
    def __init__(self, tabList, parent = None):
        super(TabWidget,self).__init__(parent)
        self.Manager = {}
        self.initUI(tabList)

    def initUI(self, args):
        for item in args:
            self.Manager[item] = Button.ButtonWidget(args[item])
        for page in self.Manager:
            self.addTab(self.Manager[page], page)

    def __getitem__(self, name):
        return self.Manager[name]


        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    funcPage1 = ['bt1', 'bt2', 'bt3']
    funcPage2 = ['bt4', 'bt5', 'bt6']
    func = {
        "page1": funcPage1,
        "page2": funcPage2
    }
    demo = TabWidget(tabList = func)
    print demo['page1']['bt1']
    demo.show()
    sys.exit(app.exec_())
