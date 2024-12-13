import time
# from pyautogui import KEYBOARD_KEYS
import pyautogui
from selenium import webdriver
# 设置Chrome浏览器的选项
options = webdriver.ChromeOptions()
options.add_argument("--autoplay-policy=no-user-gesture-required")
# 
# 启动Chrome浏览器
driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome(executable_path = "C:/Program Files (x86)/Chromebrowser/chromedriver", options=options)

# 打开网页    替换为你想要打开的网页地址
driver.get("https://www.bilibili.com/video/BV16v411L7js/?p=52&spm_id_from=pageDriver&vd_source=4d916d45f520fe0c86047578b30f742a.")  

# 等待页面加载完成
# driver.implicitly_wait(5)  # 等待10秒钟，如果页面加载完成，则继续运行下一步
time.sleep(5)
# 查找视频元素
# video = driver.find_element_by_tag_name("video")

# 发送字母"f"，模拟键盘按键
pyautogui.press('f') 
time.sleep(600)
# driver.implicitly_wait(10)
# # 播放视频
# video.play()
