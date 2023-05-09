import time

from PyQt5.QtWidgets import QSizePolicy, QWidget, QHBoxLayout, QPushButton, QApplication, QProgressBar, QVBoxLayout, QLabel
from PyQt5.QtCore import QBasicTimer, Qt, QEvent, pyqtSignal
import psutil
import sys


class KillButton(QPushButton):
    kill_signal = pyqtSignal(int)

    def __init__(self, name, pid, size):
        super(KillButton, self).__init__(name)
        self.name = name
        self.pid = pid
        self.size = size
        self.clicked.connect(self.on_button_clicked)
        # 添加 stretch factor
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def on_button_clicked(self):
        # 执行按钮点击后需要执行的操作
        print(f"{self.name} {self.pid} was killed")

        self.kill_signal.emit(self.size)
        self.parentWidget().layout().removeWidget(self)
        psutil.Process(self.pid).kill()
        self.deleteLater()

    def mouseMoveEvent(self, event):
        pass


class MemoryList(QWidget):

    closed = pyqtSignal()

    def __init__(self, process_info):
        super().__init__()
        self.total_score = 0
        self.process_info = process_info
        self.initUI()

    def initUI(self):

        # 主窗口
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("""
                    QWidget {
                        background-color: rgba(145,225,245,1);
                        border: 5px solid rgba(125, 205, 245, 0.9);
                        border-radius: 10px;
                        box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.5);
                    }
                    QProgressBar {
                        border: 2px solid rgba(0, 0, 0, 0.2);
                        border-radius: 10px;
                        background-color: rgba(255, 255, 255, 150);
                        color: rgba(0, 0, 0, 200);
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: rgba(50, 150, 250, 150);
                    }
                """)

        # 成就和分数容器
        self.score_container = QWidget()
        self.score_container.setFixedHeight(100)
        self.score_container.setStyleSheet("""
                            background-color: rgba(145,225,245,1);
                            border-radius: 10px;
                            box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.5);
                        """)
        self.score_vbox = QVBoxLayout(self.score_container)
        self.score_vbox.setAlignment(Qt.AlignCenter)

        self.score_label = QLabel("清洁分数：0")
        self.score_vbox.addWidget(self.score_label)

        self.achievement_label = QLabel("成就：初级清洁工")
        self.score_vbox.addWidget(self.achievement_label)

        vbox.addWidget(self.score_container)


        # 按钮和进度条容器
        self.hbox = QHBoxLayout()
        vbox.addLayout(self.hbox)

        # 左侧按钮容器
        btn_container = QWidget()
        btn_container.setStyleSheet("""
                            background-color: rgba(145,225,245,1);
                            box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.5);
                        """)
        btn_container.setFixedHeight(500)

        btn_vbox = QVBoxLayout(btn_container)
        btn_vbox.setContentsMargins(0, 0, 0, 0)
        btn_vbox.setSpacing(0)
        btn_vbox.setAlignment(Qt.AlignCenter)
        btn_vbox.setStretch(0, 1)

        btn_vbox.addStretch(1)
        for process in self.process_info:
            button = KillButton(process.get("name"), pid=process.get("pid"), size=process.get("size"))
            button.setStyleSheet("""
            border-radius: 0px;
            border: 2px solid rgba(125, 185, 245, 0.9);
            
            """)
            button.setFixedHeight(btn_container.height() * process.get("size") // 100)

            btn_vbox.addWidget(button)
            button.kill_signal.connect(self.on_kill_button_clicked)

        self.hbox.addWidget(btn_container)

        # 内存占用条
        self.pbar = QProgressBar(self)
        self.pbar.setOrientation(Qt.Vertical)
        self.pbar.setValue(52)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        self.pbar.setTextVisible(True)
        self.pbar.setFixedWidth(70)
        self.pbar.setFixedHeight(500)
        font = self.pbar.font()
        font.setPointSize(16)
        self.pbar.setFont(font)

        self.hbox.addWidget(self.pbar)
        vbox.addStretch(1)
        self.show()

    def on_kill_button_clicked(self, score):
        self.total_score += score
        self.score_label.setText(f"分数：{self.total_score}")
        if self.total_score < 10:
            self.achievement_label.setText(f"成就：懒惰清洁工")
        elif 10 <= self.total_score < 30:
            self.achievement_label.setText(f"成就：扫地清洁工")
        elif 30 <= self.total_score < 50:
            self.achievement_label.setText(f"成就：破烂回收工")
        elif 50 <= self.total_score < 70:
            self.achievement_label.setText(f"成就：破烂王")
        elif 70 <= self.total_score < 100:
            self.achievement_label.setText(f"成就：内存破坏者")
        elif 100 <= self.total_score:
            self.achievement_label.setText(f"成就：蓝屏见证者")

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            event.accept()
            time.sleep(0.1)
            self.closed.emit()
            self.close()  # 鼠标右键点击时关闭窗口

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragPos = None
        event.accept()

    def show_pos(self, root):
        pos = root.mapToGlobal(root.rect().bottomLeft())
        pos.setY(pos.y() - self.height() - root.height())
        self.move(pos)

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MemoryList()
    sys.exit(app.exec_())

