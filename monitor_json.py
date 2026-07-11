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

folder_path = os.path.join(BASE_DIR, "LLC_zh-CN")
old_file_path = os.path.join(BASE_DIR, "old.txt")
new_file_path = os.path.join(BASE_DIR, "new.txt")
old_strings = []
new_strings = []

def get_json_names():

    # 检查文件夹到底存不存在
    if not os.path.exists(folder_path):
        return []

    try:
        # 3. 获取并筛选 .json 文件
        json_filenames = [
            filename for filename in os.listdir(folder_path)
            if filename.lower().endswith('.json')
        ]
        return json_filenames

    except PermissionError:
        return []
        pass
    except Exception as e:
        return []
        pass


def replace_content(target_file):
    """核心替换逻辑"""
    try:
        # 当复制整个大文件夹时，文件写入可能需要时间，延迟稍微加长到 0.3 秒
        try:
            # 3. 读取 old.txt 并存入列表
            with open(old_file_path, 'r', encoding='utf-8') as f_old:
                # line.strip() 会自动裁掉每行开头和结尾的空格以及隐藏的换行符
                # if line.strip() 会跳过记事本里不小心敲出的空白行
                old_strings = [line.strip() for line in f_old if line.strip()]

            # 4. 读取 new.txt 并存入列表
            with open(new_file_path, 'r', encoding='utf-8') as f_new:
                new_strings = [line.strip() for line in f_new if line.strip()]


        except FileNotFoundError as e:
            # e.filename 会自动提取出到底缺了哪个文件
            #print(f"❌ 启动失败：在当前目录下找不到配置文件 '{os.path.basename(e.filename)}'")
            pass
        except Exception as e:
            #print(f"❌ 读取文件时发生未知错误：{e}")
            pass
        #time.sleep(0.5)

        with open(target_file, 'r', encoding='utf-8') as file:
            content = file.read()
            n = min(len(old_strings), len(new_strings))
            #print("开始比对...")
            time.sleep(0.01)
            for i in range(n):
                if old_strings[i] in content:
                    #print("比对成功！\n")
                    new_content = content.replace(old_strings[i], new_strings[i])
                    with open(target_file, 'w', encoding='utf-8') as file:
                        file.write(new_content)

    except Exception:
        pass  # 静默处理文件占用或读取错误


class JsonMonitorHandler(FileSystemEventHandler):
    def process_event(self, event_path):
        """统一事件遍历处理"""

        #print("开始处理...")

        if event_path.lower().endswith('.json'):
            replace_content(event_path)
        #file_names = get_json_names()

        # for temp_file_name in file_names:
        #     possible_file = os.path.join(event_path, temp_file_name)
        #     if os.path.exists(possible_file):
        #         replace_content(possible_file)


    def on_modified(self, event):
        self.process_event(event.src_path)

    def on_created(self, event):
        self.process_event(event.src_path)

    def on_moved(self, event):
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
    print("\n" + "-" * 30)
    # 这句非常关键，能让运行完的黑框停住，等待你按下回车再关闭
    input("按下回车键 (Enter) 退出程序...")