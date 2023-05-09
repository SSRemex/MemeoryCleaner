import sys

from ball import PixWindow
from memory_clean import get_percent_memory
from PyQt5.QtWidgets import QApplication


app = QApplication(sys.argv)
win = PixWindow()
win.show()

# 更新剩余内存
while True:
    memory_percent = get_percent_memory()
    win.update_memory_percent(memory_percent)
    QApplication.processEvents()
