# from tabnanny import verbose
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2 as cv

import numpy as np

from ui import Ui_Form


class Ui_MainWindow(object):
    def setupUi(self):
        self.MainWindow = QWidget()
        self.ui = Ui_Form()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.show()
        self.ui.start.clicked.connect(self.start_camera)
        self.ui.end.clicked.connect(self.end_camera)
        self.ui.resume.clicked.connect(self.resume_camera)


    def start_camera(self):
        self.ui.logger.append("Camera started============")
        self.video = Cap_video()
        self.video.start()
        self.video.Imageupdate.connect(self.update_image)

    def end_camera(self):
        self.ui.logger.append("Camera stopped==============")
        self.video.stop()
    
    def resume_camera(self):
        self.ui.logger.append("Camera resumed==============")
        self.video.resume()
        self.video.Imageupdate.connect(self.update_image)

    def update_image(self, image):
        self.ui.camera.setPixmap(QPixmap.fromImage(image))

    def print_log(self, message):
        self.ui.logger.append(message)


class Cap_video(QThread): 
    
    Imageupdate = pyqtSignal(QImage)
    def run(self):
        self.model = load_model(r"C:\Users\me\Desktop\dataset\asl\alphabet_dataset_Mobailnet.h5")
        self.classes = {'0': 'A','1': 'B','10': 'J','11': 'K','12': 'L','13': 'M','14': 'N','15': 'O','16': 'P','17': 'Q','18': 'R','19': 'S','2': 'Blank','20': 'T','21': 'U','22': 'V','23': 'W','24': 'X','25': 'Y','26': 'Z','3': 'C','4': 'D','5': 'E','6': 'F','7': 'G','8': 'H','9': 'I'}

        self.threadavtive = True
        self.img = 0
        capture = cv.VideoCapture(1)

        while self.threadavtive:
            ret, imageFrame = capture.read()
            if ret:
                wc = imageFrame.shape[1]//2
                hc = imageFrame.shape[0]//2
                imageFrame = cv.rectangle(imageFrame, (wc-112, hc-112), (wc+112, hc+112), (0, 255, 0), 3)

                self.img = imageFrame[hc-112:hc+112, wc-112:wc+112]
                self.predict(self.img)
                label = self.label + ' '+ self.present
                imageFrame = cv.putText(imageFrame,label, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                frame = cv.cvtColor(imageFrame, cv.COLOR_BGR2RGB)
                converttoformat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pic = converttoformat.scaled(640, 480, Qt.KeepAspectRatio)
               
                self.Imageupdate.emit(pic)

    def predict(self, img):
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img_p = img.reshape((1, 224, 224, 3)).astype('float32')/255.
        per = self.model.predict(img_p, verbose=0)
        lettel = per[0].tolist().index(per.max())
        self.label, self.present = self.classes[str(lettel)], str((per.max()*100).round(2))



            
    def stop(self):
        self.threadavtive = False
        self.wait()

    
    def resume(self):
        self.threadavtive = True
        self.start()






if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_winodw = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi()
    # main_winodw.show()
    sys.exit(app.exec_())
