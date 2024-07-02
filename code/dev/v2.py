import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor
import imageio
from PIL import ImageGrab

class GIFRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.frames = []

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.8)

        layout = QVBoxLayout()
        self.titleBar = QWidget(self)
        self.titleBar.setFixedHeight(40)
        self.titleBar.setStyleSheet("background-color: white;")

        titleLayout = QHBoxLayout()
        self.startButton = QPushButton("开始录制")
        self.startButton.setFixedSize(100, 30)
        self.startButton.clicked.connect(self.start_recording)

        self.stopButton = QPushButton("结束录制")
        self.stopButton.setFixedSize(100, 30)
        self.stopButton.clicked.connect(self.stop_recording)

        self.exitButton = QPushButton("退出")
        self.exitButton.setFixedSize(100, 30)
        self.exitButton.clicked.connect(self.close_application)

        titleLayout.addWidget(self.startButton)
        titleLayout.addWidget(self.stopButton)
        titleLayout.addWidget(self.exitButton)
        titleLayout.addStretch()

        self.titleBar.setLayout(titleLayout)
        layout.addWidget(self.titleBar)
        layout.addStretch()

        self.setLayout(layout)

        self.setGeometry(100, 100, 800, 600)
        self.show()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.record_thread = threading.Thread(target=self.record_screen)
        self.record_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_thread.join()

        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "保存GIF文件", "", "GIF Files (*.gif);;All Files (*)", options=options)
        if filePath:
            imageio.mimsave(filePath, self.frames, duration=0.1)

    def record_screen(self):
        while self.is_recording:
            x, y, w, h = self.geometry().getRect()
            screen = ImageGrab.grab(bbox=(x, y + 40, x + w, y + h))
            self.frames.append(screen)
            time.sleep(0.1)

    def close_application(self):
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = GIFRecorder()
    sys.exit(app.exec_())