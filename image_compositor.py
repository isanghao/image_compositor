# Todo: License message

import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5 import Qt, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
from os import path



class ImageCompositor(QWidget):
    def __init__(self):
        super().__init__()
        self.sourceImageList = []

        self.initUI()
        self.mQImage = None

    def getDateTaken(self, path):
        DATE_TAG = 36867
        from PIL import Image
        try:
            exif = Image.open(path)._getexif()
            return exif[DATE_TAG].split()[0].replace(':', '-')
        except:
            return ''

    def writeDateOnImage(self, cv_image, path):
        font = cv2.FONT_HERSHEY_SIMPLEX
        height, width, byte_value = cv_image.shape
        print_position = (width - 250, height - 20) #(height - 20, width - 100)
        cv2.putText(cv_image, self.getDateTaken(path), print_position, font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        print(self.getDateTaken(path))

    def rotateImage(self, cv_image):
        dst = cv2.flip(cv_image, 1).transpose([1, 0, 2])

        return dst

    def loadImage(self, path):
        print(path)
        cv_image = cv2.imread(path)

        cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB, cv_image)
        self.writeDateOnImage(cv_image, path)
        self.sourcePath = path

        height, width, byteValue = cv_image.shape
        byteValue = byteValue * width

        # TODO: Convert image to portrait

        self.sourceImageList.append(cv_image)

        if len(self.sourceImageList) == 1:
            self.setGeometry(150, 150, width, height)
            self.targetImage = cv_image.copy()
        elif len(self.sourceImageList) == 2:
            tile_long_edge = self.targetImage.shape[0]  # target image is always portrait
            tile_short_edge = int(self.targetImage.shape[1] / 2)
            for i, cv_image in enumerate(self.sourceImageList):
                cv_image = cv2.resize(cv_image, (tile_long_edge, tile_short_edge))
                cv_image = self.rotateImage(cv_image.copy())
                self.targetImage[:tile_long_edge, i*tile_short_edge:(i+1)*tile_short_edge, :] = cv_image[:tile_long_edge, :tile_short_edge, :]
        elif len(self.sourceImageList) <= 4:
            self.targetImage[:, :, :] = 255
            tile_long_edge = int(self.targetImage.shape[1] / 2)  # target image is always portrait
            tile_short_edge = int(self.targetImage.shape[0] / 2)
            for i, cv_image in enumerate(self.sourceImageList):
                cv_image = cv2.resize(cv_image, (tile_long_edge, tile_short_edge))
                tile_position_arr = [[0, 0], [0, 1], [1, 0], [1, 1]]

                x1 = tile_position_arr[i][0] * tile_long_edge
                x2 = x1 + tile_long_edge
                y1 = tile_position_arr[i][1] * tile_short_edge
                y2 = y1 + tile_short_edge
                print(cv_image.shape)
                print(cv_image[:tile_short_edge, :tile_long_edge, :].shape)
                self.targetImage[y1:y2, x1:x2, :] = cv_image[:tile_short_edge, :tile_long_edge, :]


        self.mQImage = QImage(self.targetImage, self.targetImage.shape[1], self.targetImage.shape[0], byteValue, QImage.Format_RGB888)

    def initUI(self):
        self.setGeometry(150, 150, 350, 250)
        self.setWindowTitle('Image Compositor')
        self.show()
        self.setAcceptDrops(True)
        # ToDo: Add Menu
        # Todo: Add About
        # self.loadImage(r'C:\Users\mingyuki\Downloads\cat.jpg')
        # self.loadImage(r'C:\Users\mingyuki\Downloads\Screenshot from 2018-03-07 10-16-28.png')
        # self.loadImage(r'C:\Users\mingyuki\Downloads\Screenshot from 2018-03-07 10-16-28.png')
        # self.loadImage(r'C:\Users\mingyuki\Downloads\Screenshot from 2018-03-07 10-16-28.png')
        # self.loadImage(r'C:\Users\mingyuki\Downloads\Screenshot from 2018-03-07 10-16-28.png')
        # self.loadImage(r'C:\Users\mingyuki\Pictures\Camera Roll\WIN_20180425_20_53_57_Pro.jpg')
        # self.loadImage(r'C:\Users\mingyuki\Pictures\Camera Roll\WIN_20180425_20_53_57_Pro.jpg')
        # self.loadImage(r'C:\Users\mingyuki\Pictures\Camera Roll\WIN_20180425_20_53_57_Pro.jpg')

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        if self.mQImage:
            painter.drawImage(0, 0, self.mQImage)
        painter.end()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def getOutputFileName(self):
        dir = path.split(self.sourcePath)[0]
        out_name_candiadate = ''
        for i in range(100):
            out_name_candiadate = path.join(dir, "composed_{:03d}.jpg".format(i))
            if not path.exists(out_name_candiadate):
                break
        return out_name_candiadate

    def keyPressEvent(self, event):
        # Todo: Make a explicit button for saving composed image
        if event.text() == 's':
            out_file_name = self.getOutputFileName()
            cv2.imwrite(out_file_name, cv2.cvtColor(self.targetImage, cv2.COLOR_RGB2BGR))

            QMessageBox.information(self, 'Stored', 'Composed file is stored to:\n' + out_file_name)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print('drop enter {} '.format(event.pos()) + event.mimeData().text()[8:])
        self.loadImage(event.mimeData().text()[8:])
        # Todo: Update window


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageCompositor()

    sys.exit(app.exec_())