import pyautogui
import time
# 移动到屏幕坐标(100, 150)，按下鼠标左键并保持按下
#1K=1920*1080

def MouseTrack():
    global heigh
    test =int(input("请输入1~4数字,区分4条不同轨道:"))
    if test == 1:
        heigh = 540
    elif test  ==2:
        heigh = 640
    elif test == 3:
        heigh =740
    elif test == 4:
        heigh =840
    else:
        print("输入错误")
        MouseTrack()
    print(heigh)

def Speed():
    global speed
    speed =float(input("请输入0~1数字,影响移动速度:"))
    if speed >1:
        print("输入错误")
        Speed()
    elif speed <= 1:
        print(speed)
    else:
        print("输入错误")
        Speed()
Speed()
MouseTrack()              
print(heigh)
time.sleep(1)
pyautogui.moveTo(100,heigh, duration=0.1)
pyautogui.click()
pyautogui.mouseDown()
time.sleep(1)
pyautogui.moveTo(1820, heigh, duration=speed)
time.sleep(1)
# 松开鼠标按键
pyautogui.mouseUp()
exit()