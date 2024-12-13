import pandas as pd
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

# 检查用户是否已经选中文件
if file_path == '':
    print("No file selected. Please select a file.")
else:
    df = pd.read_excel(file_path)
    df = df[df['问题分类'] != '忽略'] 
    df = df.drop(columns=['设备名称', '设备IP', '操作时间'])
    df.to_clipboard(index=False, header=False)