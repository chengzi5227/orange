import tkinter as tk
from tkinter import filedialog
import ffmpeg

def convert_to_gif(input_file, fps, scale, flags):
    output_file = input_file.rsplit('.',1)[0] + '.gif'
    try:
        ffmpeg.input(input_file).output(output_file, vf=f"fps={fps},scale={scale}:flags={flags}").run()
        print('转换完成！')
    except ffmpeg.Error as e:
        print('转换失败：', e)

def on_drop(event):
    file_path = event.data
    if file_path.endswith('.mp4'):
        convert_to_gif(file_path, fps_input.get(), scale_input.get(), flags_input.get())
    else:
        print('请选择一个MP4文件！')

# 创建窗口
window = tk.Tk()
window.title('MP4转换为GIF')
window.geometry('400x300')


# 创建拖放区域
drop_area = tk.Label(window, text='将MP4文件拖放到此区域',bg = "yellow",width=50 , height=10)
drop_area.pack(pady=50)

# 定义拖放事件处理程序
drop_area.bind('<Drop>', on_drop)


# 创建帧率输入框
fps_label = tk.Label(window, text='帧率（fps）：')
fps_label.pack()
fps_input = tk.Entry(window)
fps_input.pack()

# 创建缩放输入框
scale_label = tk.Label(window, text='缩放比例（宽度:-1）：')
scale_label.pack()
scale_input = tk.Entry(window)
scale_input.pack()

# 创建标志输入框
flags_label = tk.Label(window, text='缩放算法（lanczos）：')
flags_label.pack()
flags_input = tk.Entry(window)
flags_input.pack()

window.mainloop()