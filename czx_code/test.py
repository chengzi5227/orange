# -*- coding: utf-8 -*-
import tkinter
from tkinter import messagebox
from PIL import ImageTk, Image

window = tkinter.Tk()
window.title("随便玩玩")
window.geometry("491x492")
# 加载图片并创建Label
image = Image.open("491X492.png")
image = image.resize((491, 492), Image.ADAPTIVE)  # 调整图片大小以适应窗口
photo = ImageTk.PhotoImage(image)
label = tkinter.Label(window, image=photo)

# 设置label的位置和大小 
label.place(x=0, y=0, relwidth=1, relheight=1)

def showinfo():
    messagebox.showinfo("提示", "没用的提示")

print(123)
btn = tkinter.Button(window, text="点我就有提示", command=showinfo)
btn1 = tkinter.Button(window, text="点我就有提示2", command=showinfo)
btn.grid(column=1, row=1)
btn1.grid(column=2, row=2)

window.mainloop()