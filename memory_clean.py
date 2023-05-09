import ctypes

import win32api
import win32con
import win32process
import psutil

from process_core import ProcessList
import os
import time


# print(f"总内存：{mem.total / (1024 ** 3):.2f} GB")
# print(f"已使用内存：{mem.used / (1024 ** 3):.2f} GB")
# print(f"可用内存：{mem.available / (1024 ** 3):.2f} GB")
# print(f"内存使用率：{mem.percent}%")


# 内存使用率
def get_percent_memory():
    mem = psutil.virtual_memory()
    return mem.percent


# 弃用
def large_memory_clean():
    mem = psutil.virtual_memory()
    size = mem.total // 2
    buffer = ctypes.create_string_buffer(size)

    del buffer


# 通过EmptyWorkingSet进行所有进程的内存清理
def empty_working_set_clean():
    print("Start Empty Working Set Clean")
    pid_list = ProcessList.fast_get_all_pid_list()
    # 遍历所有进程句柄，清空各个进程的工作集
    for pid in pid_list:
        try:
            handle =  win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            win32process.SetProcessWorkingSetSize(handle, -1, -1)
            win32api.EmptyWorkingSet(handle)

        except Exception:
            continue

    print("Over Empty Working Set Clean")


if __name__ == '__main__':
    large_memory_clean()
