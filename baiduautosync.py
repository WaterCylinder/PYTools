import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import json


class BaiduSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("百度网盘同步助手")
        self.root.geometry("500x300")

        # 配置文件路径
        self.config_file = "baidu_sync_config.json"
        self.config = self.load_config()

        # 创建UI
        self.create_widgets()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"baidu_path": "", "source_path": ""}

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        """创建界面组件"""
        # 百度网盘路径选择
        tk.Label(self.root, text="百度网盘同步文件夹:").pack(pady=(20, 5), anchor='w', padx=20)

        self.baidu_path_var = tk.StringVar(value=self.config["baidu_path"])
        tk.Entry(self.root, textvariable=self.baidu_path_var, width=50).pack(padx=20, anchor='w')
        tk.Button(self.root, text="选择路径", command=self.select_baidu_path).pack(pady=(0, 10), anchor='w', padx=20)

        # 源文件夹路径选择
        tk.Label(self.root, text="需要同步的文件夹:").pack(pady=(5, 5), anchor='w', padx=20)

        self.source_path_var = tk.StringVar(value=self.config["source_path"])
        tk.Entry(self.root, textvariable=self.source_path_var, width=50).pack(padx=20, anchor='w')
        tk.Button(self.root, text="选择路径", command=self.select_source_path).pack(pady=(0, 20), anchor='w', padx=20)

        # 同步按钮
        tk.Button(self.root, text="开始同步", command=self.start_sync,
                  bg="#4CAF50", fg="white", height=2, width=15).pack(pady=10)

        # 状态标签
        self.status_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.status_var, fg="gray").pack()

    def select_baidu_path(self):
        """选择百度网盘路径"""
        path = filedialog.askdirectory(title="选择百度网盘同步文件夹")
        if path:
            self.baidu_path_var.set(path)

    def select_source_path(self):
        """选择源文件夹路径"""
        path = filedialog.askdirectory(title="选择需要同步的文件夹")
        if path:
            self.source_path_var.set(path)

    def start_sync(self):
        """开始同步文件夹"""
        baidu_path = self.baidu_path_var.get()
        source_path = self.source_path_var.get()

        if not baidu_path or not source_path:
            messagebox.showerror("错误", "请先选择两个文件夹路径！")
            return

        if not os.path.exists(baidu_path):
            messagebox.showerror("错误", "百度网盘路径不存在！")
            return

        if not os.path.exists(source_path):
            messagebox.showerror("错误", "源文件夹路径不存在！")
            return

        try:
            # 保存配置
            self.config = {
                "baidu_path": baidu_path,
                "source_path": source_path
            }
            self.save_config()

            # 复制文件夹
            folder_name = os.path.basename(source_path)
            dest_path = os.path.join(baidu_path, folder_name)

            # 如果目标已存在，先删除
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)

            shutil.copytree(source_path, dest_path)

            self.status_var.set(f"同步成功！文件已复制到: {dest_path}")
            messagebox.showinfo("成功", "文件夹同步完成！")
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BaiduSyncApp(root)
    root.mainloop()