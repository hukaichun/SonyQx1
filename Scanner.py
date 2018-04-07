#!/usr/bin/python
import Interface_User
import Interface_Dev
from PyQt4 import QtGui, QtCore
import time
import threading
import sys, os
import httplib, urlparse

BackGroundFig             = './Interface_User/pics/'
Pattern_StructedLight_Dir = './Pattern_StructedLight/'
Pattern_Calibration_Dir   = './Pattern_Calibration/'
PreviewLarge_Image_Dir    = './Large_Image/'
PreviewSmall_Image_Dir    = './Small_Image/'
Dir                       = './DCIM/'

def parseUrl(url):
    parsedUrl = urlparse.urlparse(url)
    return parsedUrl.hostname, parsedUrl.port, parsedUrl.path + "?" + parsedUrl.query, parsedUrl.path[1:]

def downloadImage(url, img_name):
    host, port, address, _ = parseUrl(url)
    conn2 = httplib.HTTPConnection(host, port)
    conn2.request("GET", address)
    response = conn2.getresponse()
    if response.status == 200:
        with open(img_name, 'wb') as img:
            img.write(response.read())
    else:
        print("ERROR: Could not download picture, error = [%d %s]" % (response.status, response.reason))
    conn2.close()

class Scanner(QtGui.QMainWindow):
    def __init__(self):
        super(Scanner, self).__init__()
        self.circleTime  = 27.5
        self.Camera      = Interface_Dev.Qx1_connect.Qx1_connection()
        self.Main        = Interface_User.Main.MainWidget(self)
        self.Arduino     = Interface_Dev.PhysicalController.PhysicalController('/dev/'+Interface_Dev.PhysicalController.getDevName(), 9600)
        self.PictureList = []
        self.connectUI()
        self.initUI()
        self.initCamera()
        self.getCameraStatusInfo()

    def initCamera(self):
        self.Camera.halfPressShutter(False)
        self.Camera.stopLiveview()

    def initUI(self):
        self.actCameraShutterIO  = False
        self.ProjectorFullScreen = False
        self.liveviewIO          = False
        self.focusIO             = False
        self.currentPatternIndex = -1
        self.exposurModeSetting()
        self.loadStructedLightPattern()
        index = self.Main['Setting3']['White Balance'].findText('Auto WB')
        self.Main['Setting3']['White Balance'].setCurrentIndex(index)
        self.setCentralWidget(self.Main)
        self.setWindowTitle('<CTWLab>  3D Scanner')


    def connectUI(self):
        self.Main['Tab'].currentChanged.connect(self.tabChanged)
        self.Main['Tab']['file'][   'Small Size'].clicked.connect(self.downloadSmall)
        self.Main['Tab']['file'][   'Large Size'].clicked.connect(self.downloadLarge)
        self.Main['Tab']['file']['Original Size'].clicked.connect(self.downloadOriginal)
        self.Main['Tab']['file'][   'Delete ALL'].clicked.connect(self.deleteAll)

        self.Main['Tab']['Truntable'][   'Direction'].clicked.connect(lambda: self.Arduino.changeTurnTableDir())
        self.Main['Tab']['Truntable'][      'Rotate'].clicked.connect(lambda: self.Arduino.turnTable())
        self.Main['Tab']['Truntable']['Rotate until'].clicked.connect(self.rotateUntill)

        self.Main['Tab']['Scan'][         'Live view'].clicked.connect(self.liveviewTrigger)
        self.Main['Tab']['Scan'][             'Focus'].clicked.connect(self.focusTrigger)
        self.Main['Tab']['Scan']['Update Camera Info'].clicked.connect(self.getCameraStatusInfo) 
        self.Main['Tab']['Scan'][        'actShutter'].clicked.connect(self.actShutter)
        self.Main['Tab']['Scan'][              'Scan'].clicked.connect(self.scanTrigger)
        
        self.Main['Tab']['Pattern Check']['Structed Light Mode'].clicked.connect(self.loadStructedLightPattern)
        self.Main['Tab']['Pattern Check'][    'Full/Sub Screen'].clicked.connect(self.changeSizeTrigger)
        self.Main['Tab']['Pattern Check'][       'Next Pattern'].clicked.connect(self.nextPatternTrigger)
        self.Main['Tab']['Pattern Check'][   'Calibration Mode'].clicked.connect(self.loadCalibrationPattern)

        self.Main['Setting3'][     'White Balance'].currentIndexChanged.connect(self.whiteBalanceSetting)
        self.Main['Setting3']['Cont Shooting Mode'].currentIndexChanged.connect(self.contShootingModeSetting)
        self.Main['Setting3'][         'Beep Mode'].currentIndexChanged.connect(self.beepModeSetting)
        self.Main['Setting1'][        'Still Size'].currentIndexChanged.connect(self.stillSizeSetting)
        self.Main['Setting1'][      'Exposur Mode'].currentIndexChanged.connect(self.exposurModeSetting)
        self.Main['Setting1'][     'Still Quality'].currentIndexChanged.connect(self.stillQualitySetting)
        self.Main['Setting2'][     'Shutter Speed'].currentIndexChanged.connect(self.shutterSpeedSetting)
        self.Main['Setting2'][         'Iso Speed'].currentIndexChanged.connect(self.isoSetting)
        self.Main['Setting2'][           'fNumber'].currentIndexChanged.connect(self.fNumberSetting)
    
    ####### Turntable #######
    def rotateUntill(self):
        deg = self.Main['Rotate Angle']['Rotate Angle'].value()
        self.Arduino.turnTable()
        time.sleep(deg * self.circleTime/360)
        self.Arduino.turnTable()

    ####### Turntable End #######


    ####### Download #######
    def downloadSmall(self):
        for x in self.PictureList:
            fileName = x['content']['original'][0]['fileName']
            self.statusBar().showMessage('download '+ fileName)
            fileName = PreviewSmall_Image_Dir + fileName
            downloadImage(x['content']['smallUrl'],
                          fileName)

    def downloadLarge(self):
        for x in self.PictureList:
            fileName = x['content']['original'][0]['fileName']
            self.statusBar().showMessage('download '+ fileName)
            fileName = PreviewLarge_Image_Dir + fileName
            downloadImage(x['content']['largeUrl'],
                          fileName)

    def downloadOriginal(self):
        for x in self.PictureList:
            fileName = x['content']['original'][0]['fileName']
            self.statusBar().showMessage('download '+ fileName)
            fileName = Dir + fileName
            downloadImage(x['content']['original'][0]['url'],
                          fileName)
        
    def deleteAll(self):
        self.Main['Tab']['file'][   'Small Size'].setEnabled(False)
        self.Main['Tab']['file'][   'Large Size'].setEnabled(False)
        self.Main['Tab']['file']['Original Size'].setEnabled(False)
        self.Main['Tab']['file'][   'Delete ALL'].setEnabled(False)
        URI = [x['uri'] for x in self.PictureList]
        self.statusBar().showMessage('Delete file')
        self.Camera.DeleteContent(URI)
    ####### Download End #######

    ####### Scan #######
    def scanTrigger(self):
        mode = str(self.Main['Setting3']['Cont Shooting Mode'].currentText())
        self.Main['Projector'].showFullScreen()
        if mode == 'Single':
            th = threading.Thread(target = self.singleShotMode)
        else:
            th = threading.Thread(target = self.contShotMode)
        th.setDaemon = True
        th.start()

    def contShotMode(self):
        beginDelay = float(self.Main['Begin Delay'][ 'Before Shutter'].value())/100
        innerDelay = float(self.Main['Inner Delay']['Between Pattern'].value())/100
        self.Main['Projector'].lock.acquire()
        try:
            self.Main['Projector'].Image = self.Main['Projector']['Pattern'][0]
        finally:
            self.Main['Projector'].lock.release()
        time.sleep(beginDelay)
        self.Arduino.actShutter()
        for imag in self.Main['Projector']['Pattern']:
            self.Main['Projector'].lock.acquire()
            try:
                self.Main['Projector'].Image = imag
            finally:
                self.Main['Projector'].lock.release()
            time.sleep(innerDelay)
        self.Arduino.releaseShutter()
                

    def singleShotMode(self):
        beginDelay = float(self.Main['Begin Delay']['Before Shutter'].value())/100
        self.Main['Projector'].lock.acquire()
        try:
            self.Main['Projector'].Image = self.Main['Projector']['Pattern'][0]
        finally:
            self.Main['Projector'].lock.release()
        time.sleep(beginDelay)
        for imag in self.Main['Projector']['Pattern']:
            self.Main['Projector'].lock.acquire()
            try:
                self.Main['Projector'].Image = imag
            finally:
                self.Main['Projector'].lock.release()
            time.sleep(0.05)
            print self.Camera.TakePicture()        
    ####### Scan End #######

    ####### Projector Functions #######
    def loadStructedLightPattern(self):
        self.currentPatternIndex = -1
        os.system('ls {} > piclist'.format(Pattern_StructedLight_Dir))
        del self.Main['Projector']['Pattern'][:]
        with open('piclist') as f:
            for line in f:
                line = Pattern_StructedLight_Dir+line.rstrip()
                self.Main['Projector']['Pattern'].append(QtGui.QImage(line))
        os.system('rm piclist')
        self.Main['Projector'].show()
        threading.Thread(target = self.marqueePattern).start()

    def loadCalibrationPattern(self):
        self.currentPatternIndex = -1
        os.system('ls {} > piclist'.format(Pattern_Calibration_Dir))
        del self.Main['Projector']['Pattern'][:]
        with open('piclist') as f:
            for line in f:
                line = Pattern_Calibration_Dir+line.rstrip()
                self.Main['Projector']['Pattern'].append(QtGui.QImage(line))
        os.system('rm piclist')
        self.Main['Projector'].show()
        threading.Thread(target = self.marqueePattern).start()

    def marqueePattern(self):
        delayTime = float(self.Main['Inner Delay']['Between Pattern'].value())/100
        for imag in self.Main['Projector']['Pattern']:
            self.Main['Projector'].lock.acquire()
            try:
                self.Main['Projector'].Image = imag
            finally:
                self.Main['Projector'].lock.release()
            time.sleep(delayTime)

    def changeSizeTrigger(self):
        self.ProjectorFullScreen = not self.ProjectorFullScreen
        if self.ProjectorFullScreen:
            self.Main['Projector'].showFullScreen()
        else:
            self.Main['Projector'].showMaximized()

    def nextPatternTrigger(self):
        self.currentPatternIndex+=1
        self.currentPatternIndex %= len(self.Main['Projector']['Pattern'])
        self.Main['Projector'].lock.acquire()
        try:
            self.Main['Projector'].Image = self.Main['Projector']['Pattern'][self.currentPatternIndex]
        finally:
            self.Main['Projector'].lock.release()
    ####### Projector Functions End #######

    ####### Camera Functions #######
    def actShutter(self):
        if str(self.Main['Setting3']['Cont Shooting Mode'].currentText()) == 'Single':
            print self.Camera.TakePicture()
        else:
            self.actCameraShutterIO = not self.actCameraShutterIO
            print self.Camera.ContShooting(self.actCameraShutterIO)
    
    def focusTrigger(self):
        self.focusIO = not self.focusIO
        if self.focusIO:
            self.Camera.FocusMode('AF-S')
            self.Camera.halfPressShutter(self.focusIO)

            self.Main['Setting1'][     'Still Quality'].setEnabled(False)
            self.Main['Setting1'][      'Exposur Mode'].setEnabled(False)
            self.Main['Setting1'][        'Still Size'].setEnabled(False)
            self.Main['Setting2'][         'Iso Speed'].setEnabled(False)
            self.Main['Setting2'][     'Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][           'fNumber'].setEnabled(False)
            self.Main['Setting3']['Cont Shooting Mode'].setEnabled(False)
            self.Main['Setting3'][         'Beep Mode'].setEnabled(False)
            self.Main['Setting3'][     'White Balance'].setEnabled(False)
        else:
            self.Camera.halfPressShutter(self.focusIO)
            self.Camera.FocusMode('MF')            
            self.Main['Setting1'][     'Still Quality'].setEnabled(True)
            self.Main['Setting1'][      'Exposur Mode'].setEnabled(True)
            self.Main['Setting1'][        'Still Size'].setEnabled(True)
            self.Main['Setting2'][         'Iso Speed'].setEnabled(True)
            self.Main['Setting2'][     'Shutter Speed'].setEnabled(True)
            self.Main['Setting2'][           'fNumber'].setEnabled(True)
            self.Main['Setting3']['Cont Shooting Mode'].setEnabled(True)
            self.Main['Setting3'][         'Beep Mode'].setEnabled(True)
            self.Main['Setting3'][     'White Balance'].setEnabled(True)
            self.exposurModeSetting()
    ####### Camera Functions End #######

    ####### Camera Setting #######
    def contShootingModeSetting(self):
        mode = str(self.Main['Setting3']['Cont Shooting Mode'].currentText())
        print self.Camera.ContinuouShootingMode(mode)

    def whiteBalanceSetting(self):
        mode = str(self.Main['Setting3']['White Balance'].currentText())
        if mode == 'Auto WB':
            print self.Camera.WhiteBalance(mode)
        else:
            print self.Camera.WhiteBalance('Color Temperature', int(mode))

    def fNumberSetting(self):
        mode = str(self.Main['Setting2']['fNumber'].currentText())
        print self.Camera.fNumber(mode)

    def isoSetting(self):
        mode = str(self.Main['Setting2']['Iso Speed'].currentText())
        print self.Camera.IsoSpeedRate(mode)

    def stillQualitySetting(self):
        mode = str(self.Main['Setting1']['Still Quality'].currentText())
        print self.Camera.StillQuality(mode)

    def shutterSpeedSetting(self):
        mode = str(self.Main['Setting2']['Shutter Speed'].currentText())
        print self.Camera.ShutterSpeed(mode)

    def exposurModeSetting(self):
        mode = str(self.Main['Setting1']['Exposur Mode'].currentText())
        print self.Camera.ExposureMode(mode)
        if mode == 'Intelligent Auto':
            self.Main['Setting2'][    'Iso Speed'].setEnabled(False)
            self.Main['Setting2']['Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][      'fNumber'].setEnabled(False)
            self.Main['Setting3']['White Balance'].setEnabled(False)
        elif mode == 'Superior Auto':
            self.Main['Setting2'][    'Iso Speed'].setEnabled(False)
            self.Main['Setting2']['Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][      'fNumber'].setEnabled(False)
            self.Main['Setting3']['White Balance'].setEnabled(False)
        elif mode == 'Program Auto':
            self.Main['Setting2'][    'Iso Speed'].setEnabled(True)
            self.Main['Setting2']['Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][      'fNumber'].setEnabled(False)
            self.Main['Setting3']['White Balance'].setEnabled(True)
        elif mode == 'Aperture':
            self.Main['Setting2'][    'Iso Speed'].setEnabled(True)
            self.Main['Setting2']['Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][      'fNumber'].setEnabled(True)
            self.Main['Setting3']['White Balance'].setEnabled(True)
        elif mode == 'Shutter':
            self.Main['Setting2'][    'Iso Speed'].setEnabled(True)
            self.Main['Setting2']['Shutter Speed'].setEnabled(True)
            self.Main['Setting2'][      'fNumber'].setEnabled(False)
            self.Main['Setting3']['White Balance'].setEnabled(True)

    def stillSizeSetting(self):
        _ = str(self.Main['Setting1']['Still Size'].currentText())
        mode = _.split(',')
        print self.Camera.StillSize(mode)
    
    def beepModeSetting(self):
        mode = str(self.Main['Setting3']['Beep Mode'].currentText())
        print self.Camera.BeepMode(mode)

    def liveviewTrigger(self):
        self.liveviewIO = not self.liveviewIO
        if self.liveviewIO:
            liveThread = threading.Thread(target = self.Liveview)
            liveThread.daemon = True
            liveThread.start()
            self.statusBar().showMessage('Start Liveview')
        else:
            self.Camera.stopLiveview()
            self.statusBar().showMessage('Stop Liveview')

    def Liveview(self):
        host, port, address, _ = parseUrl(self.Camera.liveviewUrl())
        conn3 = httplib.HTTPConnection(host, port)
        conn3.request('GET', address)
        resp  = conn3.getresponse()

        if resp.status == 200:
            buf = b''
            while self.liveviewIO:
                nextPart = resp.read(2048)
                jpegStart = nextPart.find(b'\xFF\xD8\xFF')
                jpegEnd   = nextPart.find(b'\xFF\xD9')
                if jpegEnd != -1:
                    buf+=nextPart[:jpegEnd+2]
                    self.Main['Liveview'].Image.loadFromData(buf)
                if jpegStart != -1:
                    buf = nextPart[jpegStart:]
                else:
                    buf += nextPart
            self.Main['Liveview'].Image = QtGui.QImage(BackGroundFig+'garbage.jpg')
            del buf

    def getCameraStatusInfo(self):
        time.sleep(0.5)
        r                        = self.Camera.getEvent()
        status                   = r[ 1][         'cameraStatus']
        currentCameraFunction    = r[12]['currentCameraFunction']
        if currentCameraFunction == 'Remote Shooting':
            try:
                liveviewStatus        = r[ 3][     'liveviewStatus']
                stillSize             = r[14][      'currentAspect']+','+r[14]['currentSize']
                currentBeepMode       = r[11][    'currentBeepMode']
                currentExposureMode   = r[18]['currentExposureMode']
                currentFNumber        = r[27][     'currentFNumber']
                currentFcousMode      = r[28][   'currentFocusMode']
                currentIsoSpeedRate   = r[29]['currentIsoSpeedRate']
                currentShutterSpeed   = r[32]['currentShutterSpeed']
                stillQuality          = r[37][       'stillQuality']
                contShootingMode      = r[38][   'contShootingMode']
            except:
                self.getCameraStatusInfo()
            else:
                index = self.Main['Setting2']['Iso Speed'].findText(currentIsoSpeedRate)
                if index > -1:
                    self.Main['Setting2']['Iso Speed'].setCurrentIndex(index)

                index = self.Main['Setting2']['Shutter Speed'].findText(currentShutterSpeed)
                if index > -1:
                    self.Main['Setting2']['Shutter Speed'].setCurrentIndex(index)

                index = self.Main['Setting2']['fNumber'].findText(currentFNumber)
                if index > -1:
                    self.Main['Setting2']['fNumber'].setCurrentIndex(index)

                index = self.Main['Setting1']['Still Quality'].findText(stillQuality)
                if index > -1:
                    self.Main['Setting1']['Still Quality'].setCurrentIndex(index)

                index = self.Main['Setting1']['Still Size'].findText(stillSize)
                if index > -1:
                    self.Main['Setting1']['Still Size'].setCurrentIndex(index)

                index = self.Main['Setting1']['Exposur Mode'].findText(currentExposureMode)
                if index > -1:
                    self.Main['Setting1']['Exposur Mode'].setCurrentIndex(index)

                index = self.Main['Setting3']['Cont Shooting Mode'].findText(contShootingMode)
                if index > -1:
                    self.Main['Setting3']['Cont Shooting Mode'].setCurrentIndex(index)

                index = self.Main['Setting3']['Beep Mode'].findText(currentBeepMode)
                if index > -1:
                    self.Main['Setting3']['Beep Mode'].setCurrentIndex(index)

                self.statusBar().showMessage(  "<Camera Status>: "+ status+ "  "
                                             "<Camera Function>: "+ currentCameraFunction+ "  "
                                                 "<Liveview IO>: "+ str(liveviewStatus)+ "  ")
        else:
            self.statusBar().showMessage(  "<Camera Status>: "+ status+ "  "
                                         "<Camera Function>: "+ currentCameraFunction+ "  "
                                           "<Contents Cont>: "+ str(len(self.PictureList))+ "  ")

    ####### Camera Setting End #######

    ####### Camera Function switch ####### 
    def tabChanged(self):
        index =  self.Main['Tab'].currentIndex()
        if str(self.Main['Tab'].tabText(index)) == 'Scan':
            if self.Camera.CameraFunction()['result'][0] != 'Remote Shooting':
                print self.Camera.CameraFunction('Remote Shooting')
                time.sleep(1.5)
            self.Main['Setting1'][     'Still Quality'].setEnabled(True)
            self.Main['Setting1'][      'Exposur Mode'].setEnabled(True)
            self.Main['Setting1'][        'Still Size'].setEnabled(True)
            self.Main['Setting2'][         'Iso Speed'].setEnabled(True)
            self.Main['Setting2'][     'Shutter Speed'].setEnabled(True)
            self.Main['Setting2'][           'fNumber'].setEnabled(True)
            self.Main['Setting3']['Cont Shooting Mode'].setEnabled(True)
            self.Main['Setting3'][         'Beep Mode'].setEnabled(True)
            self.Main['Setting3'][     'White Balance'].setEnabled(True)
            self.exposurModeSetting()
            self.getCameraStatusInfo()

        if str(self.Main['Tab'].tabText(index)) == 'file':
            if self.focusIO:
                self.focusTrigger()
            if self.Camera.CameraFunction()['result'][0] != 'Contents Transfer':
                print self.Camera.CameraFunction('Contents Transfer')
                time.sleep(1.5)
                if self.liveviewIO:
                    self.liveviewTrigger()
            _ = self.Camera.ContentList()
            try:
                self.PictureList = _['result'][0]
            except:
                self.PictureList = []
                self.Main['Tab']['file'][   'Small Size'].setEnabled(False)
                self.Main['Tab']['file'][   'Large Size'].setEnabled(False)
                self.Main['Tab']['file']['Original Size'].setEnabled(False)
                self.Main['Tab']['file'][   'Delete ALL'].setEnabled(False)
            else:
                self.Main['Tab']['file'][   'Small Size'].setEnabled(True)
                self.Main['Tab']['file'][   'Large Size'].setEnabled(True)
                self.Main['Tab']['file']['Original Size'].setEnabled(True)
                self.Main['Tab']['file'][   'Delete ALL'].setEnabled(True)
            self.Main['Setting1'][     'Still Quality'].setEnabled(False)
            self.Main['Setting1'][      'Exposur Mode'].setEnabled(False)
            self.Main['Setting1'][        'Still Size'].setEnabled(False)
            self.Main['Setting2'][         'Iso Speed'].setEnabled(False)
            self.Main['Setting2'][     'Shutter Speed'].setEnabled(False)
            self.Main['Setting2'][           'fNumber'].setEnabled(False)
            self.Main['Setting3']['Cont Shooting Mode'].setEnabled(False)
            self.Main['Setting3'][         'Beep Mode'].setEnabled(False)
            self.Main['Setting3'][     'White Balance'].setEnabled(False)
            self.getCameraStatusInfo()
    ####### Camera Function switch End #######

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = Scanner()
    ex.show()
    sys.exit(app.exec_())
