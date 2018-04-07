import threading
from PyQt4 import QtGui, QtCore


class ImageDisplay(QtGui.QLabel):
    def __init__(self, parent = None):
        super(ImageDisplay, self).__init__(parent)
        self.lock = threading.Lock()
        self.Image = QtGui.QImage()

    def paintEvent(self, event):
        self.lock.acquire()
        try:
            self.setPixmap(QtGui.QPixmap.fromImage(self.Image))
        finally:
            self.lock.release()
        QtGui.QLabel.paintEvent(self, event)

class ProjectorWidget(ImageDisplay):
    def __init__(self, parent = None):
        super(ProjectorWidget, self).__init__(parent)
        self.Manager = {}
        self.initUI()
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def __getitem__(self, name):
        return self.Manager[name]

    def initUI(self):
        self.Manager['Pattern'] = []
        self.setMinimumSize(640,480)
        self.setAlignment(QtCore.Qt.AlignCenter)
        

