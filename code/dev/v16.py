import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, QSlider, QDialog, QFormLayout, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
import imageio
from PIL import ImageGrab

class SettingsDialog(QDialog):
    def __init__(self, frame_rate, downsampling, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setGeometry(200, 200, 300, 200)
        
        self.frame_rate = frame_rate
        self.downsampling = downsampling
        
        layout = QFormLayout()
        
        self.frameRateEdit = QLineEdit(str(self.frame_rate))
        self.downsamplingEdit = QLineEdit(str(self.downsampling))
        
        layout.addRow("帧率", self.frameRateEdit)
        layout.addRow("降采样", self.downsamplingEdit)
        
        self.okButton = QPushButton("确定")
        self.okButton.clicked.connect(self.accept)
        
        layout.addWidget(self.okButton)
        
        self.setLayout(layout)
    
    def getValues(self):
        return int(self.frameRateEdit.text()), int(self.downsamplingEdit.text())

class GIFRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []
        self.recording_time = 0
        self.resize_margin = 10
        self.resizing = False
        self.frame_rate = 10  # Default frame rate
        self.downsampling = 1  # Default downsampling rate
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.6)

        layout = QVBoxLayout()
        self.titleBar = QWidget(self)
        self.titleBar.setFixedHeight(60)  # Adjust height to fit the new label
        self.titleBar.setStyleSheet("background-color: black;")

        titleLayout = QVBoxLayout()
        
        infoLabel = QLabel("Author：wcy    GitHub：https://github.com/chuanye-Wang")
        infoLabel.setStyleSheet("color: white; font-size: 12px;")
        infoLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        buttonLayout = QHBoxLayout()
        self.recordButton = QPushButton("开始录制")
        self.recordButton.setFixedSize(100, 30)
        self.recordButton.setStyleSheet("background-color: green; color: white;")
        self.recordButton.clicked.connect(self.toggle_recording)

        self.settingsButton = QPushButton("设置")
        self.settingsButton.setFixedSize(100, 30)
        self.settingsButton.setStyleSheet("background-color: gray; color: white;")
        self.settingsButton.clicked.connect(self.open_settings)

        self.exitButton = QPushButton("退出")
        self.exitButton.setFixedSize(100, 30)
        self.exitButton.setStyleSheet("background-color: white; color: black;")
        self.exitButton.clicked.connect(self.close_application)

        self.timeLabel = QLabel("00:00")
        self.timeLabel.setStyleSheet("color: white; font-size: 20px;")

        buttonLayout.addWidget(self.recordButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.timeLabel)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.settingsButton)
        buttonLayout.addWidget(self.exitButton)
        
        titleLayout.addWidget(infoLabel)
        titleLayout.addLayout(buttonLayout)

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
            imageio.mimsave(filePath, self.frames, duration=1/self.frame_rate)

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
            # screen = ImageGrab.grab(bbox=(x + self.resize_margin, y + 35 + self.titleBar.height() + self.resize_margin, x + w - self.resize_margin, y + h - self.resize_margin))
            screen = ImageGrab.grab(bbox=(x + self.resize_margin - 6, y + 5 + self.titleBar.height() + self.resize_margin, x + w - self.resize_margin, y + h + 6 - self.resize_margin))
            if self.downsampling > 1:
                screen = screen.resize((screen.width // self.downsampling, screen.height // self.downsampling))
            self.frames.append(screen)
            time.sleep(1 / self.frame_rate)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.frame_rate, self.downsampling, self)
        if settings_dialog.exec_():
            self.frame_rate, self.downsampling = settings_dialog.getValues()

    def close_application(self):
        self.is_recording = False
        self.timer.stop()
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join()
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_on_resize_margin(event.pos()):
                self.resizing = True
                self.drag_start_position = event.globalPos()
                self.original_geometry = self.geometry()
            else:
                self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.globalPos() - self.drag_start_position
            new_geometry = QRect(self.original_geometry)
            new_geometry.setBottomRight(new_geometry.bottomRight() + delta)
            self.setGeometry(new_geometry)
            event.accept()
        elif event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
        else:
            if self.is_on_resize_margin(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resizing = False
            event.accept()

    def is_on_resize_margin(self, pos):
        return pos.x() >= self.width() - self.resize_margin and pos.y() >= self.height() - self.resize_margin

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.is_recording:
            rect = self.rect()
            rect.setTop(self.titleBar.height())
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            
            # Draw the border outside the recording area
            pen = QPen(QColor(255, 0, 0), 5)
            painter.setPen(pen)
            border_rect = self.rect().adjusted(2, 2, -2, -2)  # Adjust the border rectangle to be outside the recorded area
            painter.drawRect(border_rect)
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