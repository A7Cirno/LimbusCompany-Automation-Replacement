import os
import sys
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 配置区 ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

old_file_path = os.path.join(BASE_DIR, "old.txt")
new_file_path = os.path.join(BASE_DIR, "new.txt")


class TaskManager:
    def __init__(self):
        # 字典：用来记录每个文件对应的倒计时器
        self.pending_timers = {}
        # 锁：防止多线程打架
        self.lock = threading.Lock()

    def schedule_task(self, target_file):
        """给变动的文件安排一个倒计时任务"""
        with self.lock:
            # 1. 如果这个文件已经在倒计时了，说明还在连续写入，取消旧的计时
            if target_file in self.pending_timers:
                self.pending_timers[target_file].cancel()

            # 2. 重新设定 1.5 秒的计时器
            timer = threading.Timer(1.5, self.replace_content, args=[target_file])
            self.pending_timers[target_file] = timer
            timer.start()

    def replace_content(self, target_file):
        """核心替换逻辑"""
        # 任务开始执行，从防抖字典里清掉记录
        with self.lock:
            if target_file in self.pending_timers:
                del self.pending_timers[target_file]

        try:
            # 1. 读取规则（每次都重新读取，支持记事本热更新）
            try:
                with open(old_file_path, 'r', encoding='utf-8') as f_old:
                    old_strings = [line.strip() for line in f_old if line.strip()]
                with open(new_file_path, 'r', encoding='utf-8') as f_new:
                    new_strings = [line.strip() for line in f_new if line.strip()]
            except Exception:
                return  # 找不到txt文件就不执行替换

            if not old_strings or not new_strings:
                return

            # 2. 读取要修改的 json 文件
            if not os.path.exists(target_file):
                return

            with open(target_file, 'r', encoding='utf-8') as file:
                content = file.read()

            original_content = content
            n = min(len(old_strings), len(new_strings))

            # 3. 核心修复：在内存中完成所有循环替换
            for i in range(n):
                if old_strings[i] in content:
                    # 注意：一定要把结果赋回给 content，这样才能累加替换结果
                    content = content.replace(old_strings[i], new_strings[i])

            # 4. 只有内容真的发生了改变，才去写入文件，防止死循环
            if content != original_content:
                with open(target_file, 'w', encoding='utf-8') as file:
                    file.write(content)

        except Exception:
            pass  # 静默处理文件占用或读取错误


# 实例化任务管理器（必须放在外层，供监控处理器调用）
task_manager = TaskManager()


# 修复：将 JsonMonitorHandler 从 TaskManager 中移出，与它平级
class JsonMonitorHandler(FileSystemEventHandler):
    def process_event(self, event_path):
        """统一事件遍历处理"""
        if event_path.lower().endswith('.json'):
            # 修复：把任务甩给防抖管理器，绝不自己阻塞去处理
            task_manager.schedule_task(event_path)

    def on_modified(self, event):
        self.process_event(event.src_path)

    def on_created(self, event):
        self.process_event(event.src_path)

    def on_moved(self, event):
        self.process_event(event.dest_path)


if __name__ == "__main__":
    event_handler = JsonMonitorHandler()
    observer = Observer()

    # 监控程序所在目录下的所有变动
    observer.schedule(event_handler, path=BASE_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    #print("\n" + "-" * 30)
    #input("按下回车键 (Enter) 退出程序...")
