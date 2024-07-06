import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QPen
import imageio
from PIL import ImageGrab

class GIFRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []
        self.recording_time = 0
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.6)

        layout = QVBoxLayout()
        self.titleBar = QWidget(self)
        self.titleBar.setFixedHeight(40)
        self.titleBar.setStyleSheet("background-color: blue;")

        titleLayout = QHBoxLayout()
        self.recordButton = QPushButton("开始录制")
        self.recordButton.setFixedSize(100, 30)
        self.recordButton.setStyleSheet("background-color: green; color: white;")
        self.recordButton.clicked.connect(self.toggle_recording)

        self.exitButton = QPushButton("退出")
        self.exitButton.setFixedSize(100, 30)
        self.exitButton.setStyleSheet("background-color: white; color: black;")
        self.exitButton.clicked.connect(self.close_application)

        self.timeLabel = QLabel("00:00")
        self.timeLabel.setStyleSheet("color: white; font-size: 20px;")

        titleLayout.addWidget(self.recordButton)
        titleLayout.addStretch()
        titleLayout.addWidget(self.timeLabel)
        titleLayout.addStretch()
        titleLayout.addWidget(self.exitButton)

        self.titleBar.setLayout(titleLayout)
        layout.addWidget(self.titleBar)
        layout.addStretch()

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_recording_time)

        self.setGeometry(100, 100, 800, 600)
        self.show()

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.recording_time = 0
        self.recordButton.setText("结束录制")
        self.recordButton.setStyleSheet("background-color: red; color: white;")
        self.record_thread = threading.Thread(target=self.record_screen)
        self.record_thread.start()
        self.set_transparency(True)
        self.timer.start(1000)  # Start the timer to update every second

    def stop_recording(self):
        self.is_recording = False
        self.record_thread.join()
        self.set_transparency(False)

        # Restore window opacity and background color
        self.setWindowOpacity(0.6)
        self.update()

        self.timer.stop()  # Stop the timer
        self.timeLabel.setText("00:00")

        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "保存GIF文件", "", "GIF Files (*.gif);;All Files (*)", options=options)
        if filePath:
            imageio.mimsave(filePath, self.frames, duration=0.1)

        self.recordButton.setText("开始录制")
        self.recordButton.setStyleSheet("background-color: green; color: white;")

    def set_transparency(self, transparent):
        if transparent:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.update()
        else:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.setWindowOpacity(1.0)  # Ensure normal opacity is restored
            self.update()

    def record_screen(self):
        while self.is_recording:
            x, y, w, h = self.geometry().getRect()
            screen = ImageGrab.grab(bbox=(x, y + 15 + self.titleBar.height(), x + w, y + h))
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

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.is_recording:
            rect = self.rect()
            rect.setTop(self.titleBar.height())
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            
            # Draw the border
            pen = QPen(QColor(255, 0, 0), 5)
            painter.setPen(pen)
            painter.drawRect(self.rect())
        else:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 255))
        super().paintEvent(event)  # Ensure the base class paintEvent is called

    def update_recording_time(self):
        self.recording_time += 1
        minutes = self.recording_time // 60
        seconds = self.recording_time % 60
        self.timeLabel.setText(f"{minutes:02d}:{seconds:02d}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = GIFRecorder()
    sys.exit(app.exec_())