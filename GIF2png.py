import os
from tkinter import Tk, filedialog, messagebox, Label, Button, Entry, StringVar, Frame
from PIL import Image, ImageSequence, ImageTk
from tkinter.ttk import Progressbar
import threading


class GIFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF 拆帧工具")
        self.root.geometry("500x300")

        # 主框架 - 用于居中对齐所有元素
        self.main_frame = Frame(root)
        self.main_frame.pack(expand=True)

        # 变量
        self.gif_path = StringVar()
        self.output_folder = StringVar()

        # GIF 文件选择部分
        gif_frame = Frame(self.main_frame)
        gif_frame.pack(pady=5)
        Label(gif_frame, text="GIF 文件:").pack(side="left", padx=5)
        Entry(gif_frame, textvariable=self.gif_path, width=40).pack(side="left", padx=5)
        Button(gif_frame, text="浏览...", command=self.browse_gif).pack(side="left", padx=5)

        # 输出文件夹选择部分
        output_frame = Frame(self.main_frame)
        output_frame.pack(pady=5)
        Label(output_frame, text="输出文件夹:").pack(side="left", padx=5)
        Entry(output_frame, textvariable=self.output_folder, width=40).pack(side="left", padx=5)
        Button(output_frame, text="浏览...", command=self.browse_output).pack(side="left", padx=5)

        # 进度条
        self.progress = Progressbar(self.main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        # 状态标签
        self.status_label = Label(self.main_frame, text="准备就绪")
        self.status_label.pack(pady=5)

        # 开始按钮
        Button(self.main_frame, text="开始拆帧", command=self.start_splitting).pack(pady=10)

        # 禁用窗口调整大小
        root.resizable(False, False)

    def browse_gif(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("GIF 文件", "*.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            self.gif_path.set(file_path)
            # 自动设置输出文件夹
            folder = os.path.join(os.path.dirname(file_path), "gif_frames")
            self.output_folder.set(folder)

    def browse_output(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder.set(folder_path)

    def start_splitting(self):
        gif_path = self.gif_path.get()
        output_folder = self.output_folder.get()

        if not gif_path:
            messagebox.showerror("错误", "请选择 GIF 文件")
            return

        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return

        # 在后台线程中执行拆帧操作
        thread = threading.Thread(
            target=self.split_gif_to_pngs,
            args=(gif_path, output_folder),
            daemon=True
        )
        thread.start()

    def split_gif_to_pngs(self, gif_path, output_folder):
        try:
            self.root.config(cursor="watch")
            self.status_label.config(text="正在处理...")
            self.progress["value"] = 0

            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)

            # 打开 GIF 文件
            with Image.open(gif_path) as img:
                # 获取总帧数
                total_frames = 0
                for frame in ImageSequence.Iterator(img):
                    total_frames += 1

                self.progress["maximum"] = total_frames

                # 重置读取指针
                img.seek(0)

                for i in range(total_frames):
                    try:
                        img.seek(i)
                        # 转换为 RGB 模式（如果是调色板模式）
                        if img.mode == 'P':
                            frame = img.convert('RGB')
                        elif img.mode == 'RGBA':
                            frame = img.convert('RGB')
                        else:
                            frame = img.copy()

                        # 保存为 PNG
                        output_path = os.path.join(output_folder, f"frame_{i + 1:04d}.png")
                        frame.save(output_path, "PNG")

                        # 更新进度
                        self.progress["value"] = i + 1
                        self.status_label.config(text=f"正在处理: {i + 1}/{total_frames}")
                        self.root.update()

                    except EOFError:
                        # 有时GIF帧数可能不准确，遇到EOF就停止
                        break

            self.status_label.config(text=f"完成! 共保存了 {self.progress['value']} 帧")
            messagebox.showinfo("完成", f"GIF 拆帧完成!\n共保存了 {self.progress['value']} 帧到:\n{output_folder}")

        except Exception as e:
            messagebox.showerror("错误", f"处理 GIF 时出错:\n{str(e)}")
            self.status_label.config(text="出错!")

        finally:
            self.root.config(cursor="")
            self.progress["value"] = 0


if __name__ == "__main__":
    root = Tk()
    app = GIFSplitterApp(root)
    root.mainloop()