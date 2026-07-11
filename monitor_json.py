import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 配置区 ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def replace_content(target_file):
    """核心替换逻辑"""
    try:
        # 当复制整个大文件夹时，文件写入可能需要时间，延迟稍微加长到 0.3 秒
        time.sleep(0.3)

        with open(target_file, 'r', encoding='utf-8') as file:
            content = file.read()

        if "黎明将至" in content:
            new_content = content.replace("黎明将至", "天将拂晓")
            with open(target_file, 'w', encoding='utf-8') as file:
                file.write(new_content)
    except Exception:
        pass  # 静默处理文件占用或读取错误


class JsonMonitorHandler(FileSystemEventHandler):
    def process_event(self, event_path):
        """统一事件处理器：无论动的是文件还是文件夹，统统拦截分析"""

        # 情况 A：直接对文件进行操作
        if os.path.isfile(event_path) and (os.path.basename(event_path) == 'Skills_personality-12.json' or os.path.basename(event_path) == 'Passives.json'):
            replace_content(event_path)

        # 情况 B：对整个文件夹进行操作（拖拽移入、复制粘贴文件夹）
        elif os.path.isdir(event_path):
            # 自动拼接路径，去该文件夹里“摸奖”看有没有 data.json
            possible_file = os.path.join(event_path, 'Skills_personality-12.json')
            if os.path.exists(possible_file):
                replace_content(possible_file)
            possible_file = os.path.join(event_path, 'Passives.json')
            if os.path.exists(possible_file):
                replace_content(possible_file)

    def on_modified(self, event):
        self.process_event(event.src_path)

    def on_created(self, event):
        self.process_event(event.src_path)

    def on_moved(self, event):
        # 移动或重命名时，目标路径 (dest_path) 才是最新的状态
        self.process_event(event.dest_path)


if __name__ == "__main__":
    event_handler = JsonMonitorHandler()
    observer = Observer()

    # --- 关键升级 2：开启递归监控 ---
    # path=BASE_DIR 表示监控 exe 所在的当前目录
    # recursive=True 表示同时监控其下方的所有子文件夹
    observer.schedule(event_handler, path=BASE_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
