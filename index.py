import tkinter as tk
from tkinter import messagebox, ttk
import os
import time
import hashlib
import psutil
import threading
import secrets
import random
import webbrowser


class AboutPage:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("关于")
        self.top.geometry("500x400")
        self.top.resizable(False, False)

        try:
            self.top.iconbitmap('app.ico')
        except:
            pass

        self.create_widgets()

    def create_widgets(self):

        title_label = tk.Label(self.top, text="全凭天意点名工具", font=("微软雅黑", 20, "bold"))
        title_label.pack(pady=20)


        version_label = tk.Label(self.top, text="版本: 1.0.0", font=("微软雅黑", 10))
        version_label.pack(pady=5)


        ttk.Separator(self.top, orient='horizontal').pack(fill='x', padx=50, pady=10)


        author_frame = tk.Frame(self.top)
        author_frame.pack(pady=10)

        tk.Label(author_frame, text="作者: ", font=("微软雅黑", 10)).grid(row=0, column=0, sticky='e')
        tk.Label(author_frame, text="hmao", font=("微软雅黑", 10)).grid(row=0, column=1, sticky='w')

        tk.Label(author_frame, text="联系方式: ", font=("微软雅黑", 10)).grid(row=1, column=0, sticky='e')
        tk.Label(author_frame, text="i@hecat.cn", font=("微软雅黑", 10)).grid(row=1, column=1, sticky='w')


        copyright_label = tk.Label(self.top,
                                   text="版权所有 © hmao",
                                   font=("微软雅黑", 10))
        copyright_label.pack(pady=15)

        github_frame = tk.Frame(self.top)
        github_frame.pack(pady=10)

        tk.Label(github_frame, text="开源地址: ", font=("微软雅黑", 10)).grid(row=0, column=0)

        github_link = tk.Label(github_frame, text="GitHub仓库",
                               font=("微软雅黑", 10), fg="blue", cursor="hand2")
        github_link.grid(row=0, column=1)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/hsmaocn/roll_call_assistant"))


        close_button = tk.Button(self.top, text="关闭",
                                 command=self.top.destroy,
                                 font=("微软雅黑", 12),
                                 width=10)
        close_button.pack(pady=20)


class RollCallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全凭天意点名工具")
        self.root.geometry("700x650")
        self.root.resizable(False, False)

        # 使用随机变量组合
        self.random_sources = {
            'last_click': (0, 0),
            'cpu_usage': 0,
            'secrets_token': ""
        }

        # 事件绑定
        self.root.bind("<Button-1>", self.record_click)

        # 学生名单
        self.student_file = "students.txt"
        self.students = self.load_students()
        self.last_called = None

        # 启动系统监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()

        self.create_widgets()

    def monitor_system(self):
        """监控系统并更新安全随机源"""
        while True:
            self.random_sources['cpu_usage'] = psutil.cpu_percent(interval=0.1)
            self.random_sources['secrets_token'] = secrets.token_hex(16)
            time.sleep(0.01)

    def record_click(self, event):
        """记录鼠标点击位置"""
        self.random_sources['last_click'] = (event.x, event.y)

    def get_secure_randomness(self):
        """生成随机组合"""
        combined = (
            f"{self.random_sources['last_click']}"
            f"{self.random_sources['cpu_usage']}"
            f"{self.random_sources['secrets_token']}"
            f"{secrets.token_hex(4)}"
            f"{time.time_ns()}"
        )
        return combined.encode('utf-8')

    def load_students(self):
        """从文件加载学生名单"""
        if not os.path.exists(self.student_file):
            with open(self.student_file, "w", encoding="utf-8") as f:
                f.write("张三\n李四\n王五\n赵六\n钱七\n孙八\n周九\n吴十")
            messagebox.showinfo("提示", f"已经创建用于演示的学生名单文件: {self.student_file}")

        try:
            with open(self.student_file, "r", encoding="utf-8") as f:
                students = [line.strip() for line in f.readlines() if line.strip()]
            random.shuffle(students)
            return students
        except Exception as e:
            messagebox.showerror("好像有点问题", f"我无法读取学生名单文件: {e}")
            return []

    def create_widgets(self):
        """创建界面"""

        title_label = tk.Label(self.root, text="要点到谁呢？", font=("微软雅黑", 24))
        title_label.pack(pady=20)

        self.result_label = tk.Label(self.root, text="等待点名...",
                                     font=("微软雅黑", 100), fg="black")
        self.result_label.pack(pady=40)

        self.call_button = tk.Button(self.root, text="开始点名",
                                     command=self.start_call_process,
                                     font=("微软雅黑", 24),
                                     bg="#4CAF50",
                                     fg="white",
                                     height=2,
                                     width=10)
        self.call_button.pack(pady=30)
        self.progress = ttk.Progressbar(self.root, orient="horizontal",
                                        length=400, mode="determinate")
        edit_button = tk.Button(self.root, text="编辑学生名单",
                                command=self.edit_students,
                                font=("微软雅黑", 12))
        edit_button.pack(pady=5)
        about_button = tk.Button(self.root, text="关于",
                                 command=self.show_about_page,
                                 font=("微软雅黑", 12))
        about_button.pack(pady=5)
        self.status_var = tk.StringVar()
        self.status_var.set(f"共 {len(self.students)} 名学生 | 真随机模式")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1,
                              relief=tk.SUNKEN, anchor=tk.W, font=("微软雅黑", 10))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def start_call_process(self):
        """开始点名"""
        if not self.students:
            messagebox.showwarning("额", "学生名单都是空的，请先添加学生")
            return

        self.call_button.config(state=tk.DISABLED)
        self.progress.pack(pady=20)
        self.result_label.config(text="随机选择中...")
        self.root.update()
        self.animate_selection()

    def animate_selection(self):
        """随机选择动画"""
        duration = 0.3
        steps = 20
        interval = duration / steps

        self.progress["value"] = 0
        self.progress["maximum"] = steps

        for i in range(steps):
            temp_name = self.generate_secure_name()
            self.result_label.config(text=temp_name)
            self.progress["value"] = i + 1
            self.root.update()
            time.sleep(interval * (0.3 + 0.7 * i / steps))

        selected = self.generate_secure_name()
        self.last_called = selected
        self.result_label.config(text=selected, fg="black")
        self.status_var.set(f"当前点到: {selected} (共 {len(self.students)} 人)")

        random.shuffle(self.students)
        self.progress.pack_forget()
        self.call_button.config(state=tk.NORMAL)

    def generate_secure_name(self):
        """使用secrets增强的安全随机选择"""
        random_data = self.get_secure_randomness()
        hash_digest = hashlib.sha256(random_data).hexdigest()
        random_index = int(hash_digest, 16) % len(self.students)
        return self.students[random_index]

    def edit_students(self):
        """编辑学生名单"""
        try:
            os.startfile(self.student_file)
        except:
            try:
                os.system(f"open {self.student_file}")
            except:
                try:
                    os.system(f"xdg-open {self.student_file}")
                except:
                    messagebox.showinfo("提示", f"请手动编辑文件: {self.student_file}")

        self.students = self.load_students()
        self.status_var.set(f"共 {len(self.students)} 名学生 | 真随机模式")

    def show_about_page(self):
        """显示关于页面"""
        AboutPage(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = RollCallApp(root)
    root.mainloop()