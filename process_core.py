import time
import psutil
import os
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed


mem = psutil.virtual_memory()


class Process:
    def __init__(self, info):
        self.pid = info.get("pid")
        self.name = info.get("name").split(".")[0]
        self.username = info.get("username")
        self.status = info.get("status")
        self.memory_usage = info.get("memory_usage")
        self.info = info

    def get_pid(self):
        return self.pid

    def get_info(self):
        return self.info

    def print(self):
        print(f"{self.pid:<10} {self.name:<25} {self.username:<15} {self.status:<15} \
        {self.memory_usage:<15}")


class ProcessList:
    def __init__(self):
        self.username = os.getlogin()
        self.processes = []
        self.flush_processes()

    @staticmethod
    def fast_get_all_pid_list():
        return psutil.pids()

    def get_list(self):
        return self.processes

    def get_process_info(self):
        total = 0
        for process in self.processes:
            total += process.memory_usage
        process_info = []
        for process in self.processes[:15]:
            size = int(process.memory_usage / total * 100)
            process_info.append({
                "name": process.name,
                "pid": process.pid,
                "size": 5 if size < 5 else size,
            })

        return process_info

    def flush_processes(self):
        pid_set = set()
        self.processes = []
        # 只遍历正在运行的进程
        for pid in psutil.pids():
            if pid in pid_set:
                continue
            try:
                proc = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            # 只处理父进程
            proc_p = proc.parent()
            if proc_p is not None:
                proc = proc_p
                if proc.pid in pid_set:
                    continue

            pid_set.add(proc.pid)

            # 生成进程信息
            process_info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'memory_info'])
            process_info["memory_usage"] = process_info['memory_info'].rss / (1024 * 1024)
            process_info["memory_usage"] = round(process_info["memory_usage"], 2)

            try:
                self.processes.append(Process(process_info))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 对生成的进程信息按内存使用量排序
        self.processes = sorted(self.processes, key=lambda p: p.memory_usage, reverse=True)

    def print_all(self):
        # 打印应用程序列表
        print("应用程序：")
        print(f"{'PID':<10} {'进程名':<25} {'用户名':<15} {'状态':<15} {'内存占用量(MB)':<15}")
        print("-" * 120)
        for process in self.processes:
            if process.status == "running" and process.username and self.username in process.username:
                process.print()

    def kill_process(self, pid):
        for p in self.processes:
            if pid == p.pid:
                p.kill()


if __name__ == '__main__':
    p_l = ProcessList()
    p_l.print_all()
    # print(p_l.fast_get_all_pid_list())
