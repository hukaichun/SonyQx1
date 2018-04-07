import datetime
import json, httplib, urlparse

headers = {"Content-type": "text/plain", "Accept": "*/*", "X-Requested-With": "com.sony.playmemories.mobile"}

class Qx1_connection(httplib.HTTPConnection, object):
    def __init__(self):
        self.postView = False
        self.pId = 0
        
        print 'Qx1 connecting ...',
        super(Qx1_connection, self).__init__(host = '192.168.122.1', port = 8080)
        resp = self("camera",{"method": "getVersions", "params": []})
        if resp['result'][0][0] != "1.0":
            self.exitWithError("Unsupported version")
        self.setDate()
        print 'ok'

    def exitWithError(self, message):
        print "Error : {}".format(message)
        self.close()


    def __call__(self, target, req):
        self.pId += 1
        req["id"] = self.pId
        #print "[REQUEST] {} {}".format(target, req)
        self.request("POST", "/sony/"+target, json.dumps(req), headers)
        self.response = self.getresponse()
        self.data = json.loads(self.response.read().decode("UTF-8"))
        #print "[RESPONSE] {}".format(self.data)
        if self.data["id"] != self.pId:
            print "ERROR: Response id dose not match"
            return {}
        if "error" in self.data:
            print("WARNING: Response contains error code: %d; error message: [%s]" % tuple(self.data["error"]))
            print "From {}".format(req)
        return self.data

    
    def liveviewUrl(self):
        resp = self('camera',{ 'method': 'startLiveview', 
                               'params': [], 
                              'version': '1.0'})
        return resp['result'][0]

    def stopLiveview(self):
        self('camera',{ 'method': 'stopLiveview', 
                        'params': [], 
                       'version': '1.0'})

    def notIDLE(self):
        return self.getEvent()[1]['cameraStatus'] != 'IDLE'

    def halfPressShutter(self,io):
        if io==True:
            self('camera',{ 'method': 'actHalfPressShutter', 
                            'params': [], 
                           'version': '1.0'})
        else:
            self('camera', { 'method': 'cancelHalfPressShutter', 
                             'params': [], 
                            'version': '1.0'})

    def getEvent(self):
        resp = self('camera',{ 'method': 'getEvent', 
                               'params': [False], 
                              'version': '1.2'})
        return resp['result']

    def FocusMode(self, mode = None):
        '''
        AF-S, MF
        '''
        if(mode != None):
            return self('camera',{ 'method': 'setFocusMode', 
                                   'params': [mode], 
                                  'version': '1.0'})
            mode = None
        else:
            return self('camera',{ 'method': 'getFocusMode', 
                                   'params': [], 
                                  'version': '1.0'})
            

    def ContinuouShootingMode(self, mode = None):
        '''
        Single, Continuous, Spd Priority Cont.
        '''
        if mode != None:
            return self('camera',{ 'method': 'setContShootingMode', 
                                   'params': [{'contShootingMode':mode}],
                                  'version': '1.0'})
        else:
            return self('camera',{ 'method': 'getContShootingMode', 
                                   'params': [], 
                                  'version': '1.0'})

    def ContShooting(self, io):
        if io:
            self('camera',{ 'method': 'startContShooting',
                            'params': [],
                           'version': '1.0'})
        else:
            self('camera',{ 'method': 'stopContShooting',
                            'params': [],
                           'version': '1.0'})

    def TakePicture(self):
        return self('camera',{ 'method': 'actTakePicture',
                               'params': [],
                              'version': '1.0'})

    def CameraFunction(self, mode = None):
        '''
        Remote Shooting, Contents Transfer
        '''
        if mode!=None:
            return self('camera',{ 'method': 'setCameraFunction', 
                                   'params': [mode], 
                                  'version': '1.0'})
            mode = None
        else:
            return self('camera',{ 'method': 'getCameraFunction', 
                                   'params': [],
                                  'version': '1.0'})
    
    def IsoSpeedRate(self, iso = None):
        '''
        AUTO, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600,
        2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000
        '''
        if iso!=None:
            return self('camera',{ 'method': 'setIsoSpeedRate', 
                                   'params': [iso],
                                  'version': '1.0'})
        else:
            return self('camera',{ 'method': 'getIsoSpeedRate',
                                   'params': [], 
                                  'version': '1.0'})

    def ShutterSpeed(self, speed=None):
        '''
        30", 25", 20", 15", 13", 10", 8", 6", 5", 4", 3.2", 2.5", 2", 1.6", 1.3", 
        1", 0.8", 0.6", 0.5", 0.4", 1/3, 1/4, 1/5, 1/6, 1/8, 1/10, 1/13, 1/15,
        1/20, 1/25, 1/30, 1/40, 1/50, 1/60, 1/80, 1/100, 1/125, 1/160, 1/200,
        1/250, 1/320, 1/400, 1/500, 1/640, 1/800, 1/1000, 1/1250, 1/1600, 1/2000,
        1/2500, 1/3200, 1/4000
        '''
        if speed != None:
            return self('camera',{ 'method': 'setShutterSpeed', 
                                   'params': [speed],
                                  'version': '1.0'})
        else:
            return self('camera',{ 'method': 'getShutterSpeed', 
                                   'params': [],
                                  'version': '1.0'})
    
    def fNumber(self, num = None):
        '''
        1.8, 2.0, 2.2, 2.5, 2.8, 3.2, 3.5, 4.0, 4.5, 5.0, 5.6, 
        6.3, 7.1, 8.0, 9.0, 10, 11, 13, 14, 16, 18, 20, 22
        '''
        if num != None:
            return self('camera', { 'method': 'setFNumber',
                                    'params': [num], 
                                   'version': '1.0'})
        else:
            return self('camera', { 'method': 'getFNumber', 
                                    'params': [],
                                   'version': '1.0'})
            

    def StillQuality(self, quality=None):
        '''
        RAW+JPEG, Fine, Standard
        '''
        if quality!=None:
            return self('camera',{ 'method': 'setStillQuality', 
                                   'params': [{'stillQuality':quality}],
                                  'version': '1.0'})
        else:
            return self('camera',{ 'method': 'getStillQuality',
                                   'params': [],
                                  'version': '1.0'})

    def ExposureMode(self, mode = None):
        '''
        Intelligent Auto, Superior Auto, Program Auto, Aperture, Shutter
        '''
        if mode != None:
            return self('camera',{ 'method': 'setExposureMode', 
                                   'params': [mode], 
                                  'version': '1.0'})
            mode = None
        else:
            return self('camera',{ 'method': 'getExposureMode',
                                   'params': [], 
                                  'version': '1.0'})
    
    def StillSize(self, size = None):
        '''
        ['3:2', '20M'], ['3:2', '10M'], ['3:2', '5.0M'], 
        ['16:9', '17M'], ['16:9', '8.4M'], ['16:9', '4.2M']
        '''
        if size != None:
            return self('camera',{ 'method': 'setStillSize', 
                                   'params': size,
                                  'version': '1.0'})
        else:
            return self('camera',{ 'method': 'getStillSize',
                                   'params': [], 
                                  'version': '1.0'})

    def BeepMode(self, mode = None):
        '''
        On, Off, Shutter Only
        '''
        if mode != None:
            return self('camera',{ 'method': 'setBeepMode',
                                   'params': [mode],
                                  'version': '1.0'})
            mode = None
        else:
            return self('camera',{ 'method': 'getBeepMode', 
                                   'params': [],
                                  'version': '1.0'})

    def WhiteBalance(self, mode = None, temperature = None):
        '''
        Auto WB, Daylight, Shade, Cloudy, Incandescent, 
        Fluorescent:Warm White (-1), 
        Fluorescent:Cool White (0), 
        Fluorescent:Day White (+1),
        Fluorescent:Daylight (+2), 
        Color Temperature [9900, 2500, 100],
        Flash, Custom, Custom 1, Custom 2, Custom3
        '''
        if mode != None:
            if temperature != None:
                return self('camera',{ 'method': 'setWhiteBalance', 
                                       'params': [mode, True, temperature],
                                      'version': '1.0'})
                temperature = None
            else:
                return self('camera',{ 'method': 'setWhiteBalance',
                                       'params': [mode, False, 2500], 
                                      'version': '1.0'})
            mode = None
        else:
            return self('camera',{ 'method': 'getWhiteBalance', 
                                   'params': [],
                                  'version': '1.0'})
    def ContentList(self):
        return self('avContent', { 'method': "getContentList",
                                   'params': [{'uri'   : 'storage:memoryCard1',
                                               'stIdx' : 0,
                                               'cnt'   : 100,
                                               'view'  : 'flat',
                                               'sort'  : ''}],
                                  'version': '1.3'})

    def DeleteContent(self, URI):
        return self('avContent', { 'method': 'deleteContent',
                                   'params': [{'uri':URI}],
                                  'version': '1.1'})
        

    def setDate(self):
        time = datetime.datetime.now().isoformat().split('.')[0]+"Z"
        return self('system',{ 'method': 'setCurrentTime', 
                               'params': [{'dateTime'             : time, 
                                           'timeZoneOffsetMinute' : 0, 
                                           'dstOffsetMinute'      : 0}], 
                              'version': '1.0'})

    

if __name__ == "__main__":
    q = Qx1_connection()
else:
    pass 
