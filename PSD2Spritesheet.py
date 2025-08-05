import os
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
from psd_tools import PSDImage


class PSDToSpritesheetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PSD 转 Spritesheet 工具")
        self.root.geometry("500x400")

        # 变量
        self.psd_path = StringVar()
        self.output_path = StringVar(value="spritesheet.png")
        self.columns = IntVar(value=5)
        self.spacing = IntVar(value=2)
        self.bg_transparent = BooleanVar(value=True)
        self.bg_color = StringVar(value="#FFFFFF")

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # PSD 文件选择
        Label(self.root, text="PSD 文件:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        Entry(self.root, textvariable=self.psd_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        Button(self.root, text="浏览...", command=self.browse_psd).grid(row=0, column=2, padx=5, pady=5)

        # 输出文件
        Label(self.root, text="输出文件:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        Entry(self.root, textvariable=self.output_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        Button(self.root, text="浏览...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 参数设置
        Label(self.root, text="参数设置").grid(row=2, column=0, columnspan=3, pady=10)

        Label(self.root, text="每行列数:").grid(row=3, column=0, padx=10, pady=5, sticky=W)
        Spinbox(self.root, from_=1, to=20, textvariable=self.columns, width=5).grid(row=3, column=1, sticky=W)

        Label(self.root, text="图层间距:").grid(row=4, column=0, padx=10, pady=5, sticky=W)
        Spinbox(self.root, from_=0, to=20, textvariable=self.spacing, width=5).grid(row=4, column=1, sticky=W)

        # 背景设置
        Checkbutton(self.root, text="透明背景", variable=self.bg_transparent,
                    command=self.toggle_bg_color).grid(row=5, column=0, padx=10, pady=5, sticky=W)

        Label(self.root, text="背景颜色:").grid(row=6, column=0, padx=10, pady=5, sticky=W)
        Entry(self.root, textvariable=self.bg_color, width=10, state=DISABLED).grid(row=6, column=1, sticky=W)
        Button(self.root, text="选择颜色", command=self.choose_color, state=DISABLED).grid(row=6, column=2, padx=5,
                                                                                           sticky=W)
        self.bg_color_entry = self.root.grid_slaves(row=6, column=1)[0]
        self.bg_color_button = self.root.grid_slaves(row=6, column=2)[0]
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # 处理按钮
        generate_btn = (Button(self.root, text="生成 Spritesheet", command=self.process_psd,
                              height=2, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
                        .grid(row=7, column=0, columnspan=3, pady=20, ipadx=20, sticky='nsew'))
        # 状态栏
        self.status = Label(self.root, text="准备就绪", bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(row=8, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

    def toggle_bg_color(self):
        if self.bg_transparent.get():
            self.bg_color_entry.config(state=DISABLED)
            self.bg_color_button.config(state=DISABLED)
        else:
            self.bg_color_entry.config(state=NORMAL)
            self.bg_color_button.config(state=NORMAL)

    def choose_color(self):
        from tkinter.colorchooser import askcolor
        color = askcolor(title="选择背景颜色")[1]
        if color:
            self.bg_color.set(color)

    def browse_psd(self):
        filepath = filedialog.askopenfilename(
            title="选择 PSD 文件",
            filetypes=[("PSD 文件", "*.psd"), ("所有文件", "*.*")]
        )
        if filepath:
            self.psd_path.set(filepath)
            # 自动设置输出文件名
            dirname, filename = os.path.split(filepath)
            name, ext = os.path.splitext(filename)
            self.output_path.set(os.path.join(dirname, f"{name}_spritesheet.png"))

    def browse_output(self):
        filepath = filedialog.asksaveasfilename(
            title="保存 Spritesheet",
            defaultextension=".png",
            filetypes=[("PNG 图像", "*.png"), ("所有文件", "*.*")],
            initialfile=self.output_path.get()
        )
        if filepath:
            self.output_path.set(filepath)

    def process_psd(self):
        if not self.psd_path.get():
            messagebox.showerror("错误", "请先选择 PSD 文件")
            return

        try:
            self.status.config(text="处理中...")
            self.root.update()

            # 获取背景颜色
            if self.bg_transparent.get():
                bg_color = (0, 0, 0, 0)
            else:
                color = self.bg_color.get()
                bg_color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) + (255,)

            # 调用处理函数
            create_spritesheet_from_psd(
                self.psd_path.get(),
                self.output_path.get(),
                columns=self.columns.get(),
                spacing=self.spacing.get(),
                background_color=bg_color
            )

            messagebox.showinfo("成功", f"Spritesheet 已生成:\n{self.output_path.get()}")
            self.status.config(text="处理完成")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败:\n{str(e)}")
            self.status.config(text="处理失败")
            raise e


def create_spritesheet_from_psd(psd_path, output_path, columns=None, spacing=0, background_color=(0, 0, 0, 0)):
    """
    将PSD文件的图层排列成精灵图(spritesheet)
    """
    # 加载PSD文件
    psd = PSDImage.open(psd_path)

    # 获取所有可见图层
    layers = [layer for layer in psd if layer.is_visible()]

    if not layers:
        raise ValueError("没有找到可见图层!")

    # 确定每个图层的尺寸(取所有图层的最大宽高)
    max_width = max(layer.width for layer in layers)
    max_height = max(layer.height for layer in layers)

    # 计算网格布局
    layer_count = len(layers)
    if columns is None:
        # 自动计算接近正方形的列数
        columns = int(round((layer_count) ** 0.5))

    rows = (layer_count + columns - 1) // columns

    # 计算总图像尺寸
    total_width = columns * (max_width + spacing) - spacing
    total_height = rows * (max_height + spacing) - spacing

    # 创建新图像
    spritesheet = Image.new('RGBA', (total_width, total_height), background_color)

    # 排列图层
    for i, layer in enumerate(layers):
        # 计算位置
        row = i // columns
        col = i % columns

        x = col * (max_width + spacing)
        y = row * (max_height + spacing)

        # 将图层转换为PIL图像
        layer_image = layer.topil()

        # 计算居中位置
        offset_x = (max_width - layer.width) // 2
        offset_y = (max_height - layer.height) // 2

        # 粘贴图层到精灵图上
        spritesheet.paste(layer_image, (x + offset_x, y + offset_y), layer_image)

    # 保存结果
    spritesheet.save(output_path)


if __name__ == "__main__":
    root = Tk()
    app = PSDToSpritesheetApp(root)
    root.mainloop()