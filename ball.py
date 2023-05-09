import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QEasingCurve, QPointF, QSize
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter
import PyQt5.QtCore as QtCore

from process_game import MemoryList
from process_core import ProcessList
from memory_clean import empty_working_set_clean

import concurrent.futures


# 内存球
class PixWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

        # 蒙版
        self.pix = QPixmap('./static/ball.png')
        window_width = 100
        window_height = 100
        self.resize(window_width, window_height)
        self.pix = self.pix.scaled(int(window_width), int(window_height),
                                   aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.setMask(self.pix.mask())

        # 设置无边框和置顶窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.__mouse_down = False
        self.__mouse_pos = None

        self.memory_list_window = None

        # 内存占用
        self.memory_percent = "0%"
        self._angle = 0
        self._center = QPointF(0, 0)
        self._size = QSize(0, 0)

        # 创建透明度动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0.1)
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.finished.connect(self.on_animation_finished)

    # 打开杀进程窗口
    def open_memory_list(self):

        if self.memory_list_window is not None:
            self.memory_list_window.close()

        pl = ProcessList()
        self.memory_list_window = MemoryList(pl.get_process_info())
        self.memory_list_window.closed.connect(lambda: setattr(self, "memory_list_window", None))
        self.memory_list_window.show_pos(self)

    # 绘制窗口
    def paintEvent(self, event):
        paint = QPainter(self)

        paint.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)

        # 在pix的中心绘制数字
        font = paint.font()
        font.setPointSize(10)
        font.setBold(True)
        paint.setFont(font)
        paint.setPen(Qt.darkBlue)
        text = self.memory_percent
        text_rect = paint.boundingRect(self.rect(), Qt.AlignCenter, text)
        paint.drawText(text_rect, Qt.AlignCenter, text)

    def update_memory_percent(self, memory_percent):
        self.memory_percent = f"{memory_percent}%"
        if self.memory_list_window is not None:
            self.memory_list_window.pbar.setValue(int(memory_percent))
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                self.animation.start()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(empty_working_set_clean)
                self.__mouse_down = False

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        self.__mouse_down = True
        if event.button() == Qt.LeftButton:
            self.__mouse_pos = event.pos()
        if event.button() == Qt.RightButton:
            self.open_memory_list()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.__mouse_down:
            self.move(self.pos() + (event.pos() - self.__mouse_pos))
            if self.memory_list_window is not None:
                self.memory_list_window.show_pos(self)

    def on_animation_finished(self):
        self.setProperty("windowOpacity", 1.0)
        self.style().unpolish(self)
        self.style().polish(self)

