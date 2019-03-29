#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

In the example, we draw randomly 1000 red points 
on the window.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer
import sys, random
import pyaudio
import numpy as np
import threading
import atexit

class Example(QWidget):
    
    def __init__(self, micobj):
        super().__init__()
        
        self.pt_x_dist = 5
        self._micobj = micobj
        self.pts = np.zeros(300)
        self.initUI()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_new_data)
        self.timer.start(100)
        
    def handle_new_data(self):
        self.update()
        
    def initUI(self):      

        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle('Points')
        self.show()
        

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()


    def drawPoints(self, qp):
      
        qp.setPen(Qt.red)
        size = self.size()
        
        num_pts = size.width() // self.pt_x_dist
        pts = self._micobj.get_frames()

        if np.size(np.shape(pts)) == 2:
            print(np.max(pts))
            pts = np.reshape(pts, (np.size(pts)))
        self.pts = np.hstack((self.pts, pts))
        self.pts = self.pts[-num_pts:]
        y = self.pts[0] + size.height()//2
        for i in range(num_pts):
            x = i*self.pt_x_dist
            x2 = (i+1)*self.pt_x_dist
            y2 = self.pts[num_pts-i-1] + size.height()//2
            qp.drawLine(x, y, x2, y2)
            y = y2
                
        
class MicRec(object):
    def __init__(self, rate=4000, chunksize=1024):
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.frombuffer(data, dtype='int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue
    
    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames
    
    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    micobj = MicRec()
    ex = Example(micobj)
    micobj.start()
    sys.exit(app.exec_())

