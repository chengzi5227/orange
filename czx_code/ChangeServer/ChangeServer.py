import configparser
import ctypes
import subprocess
import sys
import psutil
import os
# import messagebox
import tkinter
from tkinter import messagebox

#授权管理员
def run_as_admin():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise ctypes.WinError()
    except:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def kill_process(process_name):
    try:
        output = subprocess.check_output(["pgrep", process_name])
        pids = output.splitlines()
        for pid in pids:
            subprocess.call(["kill", pid])
        print("进程 {} 已被成功杀死".format(process_name))
    except subprocess.CalledProcessError:
        print("没有名为 {} 的进程".format(process_name))


#手动版切环境
def find_directory(target_process_name):
    # 获取所有进程列表
    process_list = psutil.process_iter()
    # print(process_list)
    # 要查找的进程名
    #target_process_name = "your_process_name"

    # 遍历进程列表
    for p in process_list:
        # 获取进程的名称
        process_name = p.name()

        # 如果进程名称匹配到要查找的进程名
        if target_process_name in process_name:
            # 获取进程的根目录
            global process_root_directory
            process_root_directory = os.path.dirname(p.exe())

            # 打印根目录路径
            print(f"The root directory of {target_process_name} is: {process_root_directory}")
            break
    #匹配不到在线进程
    if len(process_root_directory) == 0:
        print('查询进程未启动，请检查后再运行')
        window1 = tkinter.Tk()
        window1.withdraw()
        top = tkinter.Toplevel(window1)
        top.title('置顶提示')
        top.attributes('-topmost', True)
        messagebox.showinfo('提示', '查询进程未启动，请检查后再运行！')
        window1.deiconify()
        exit()


def find_server(directory,process):
    filename = "server.ini"
    ini_file = os.path.join(directory, filename)
    #修改访问权限
    os.chmod(ini_file, 0o666)
    # 创建ConfigParser对象并读取INI文件内容
    config = configparser.ConfigParser()
    config.read(ini_file)
    # 修改INI文件的内容
    if process ==1:
        config.set('server', 'host', 'pre.raylink.live')
        config.set('sso', 'host', 'sso-pre.renderbus.com')
        config.set('web', 'host', 'console-pre.raylink.live')
        config.set('verify', 'biz', '888')
        config.set('verify', 'accessId', 'QHLZV6eQ9cpkSA7n8ighRZu')
    elif process ==2:
        config.set('server', 'host', 'api.raylink.live')
        config.set('sso', 'host', 'sso.renderbus.com')
        config.set('web', 'host', 'console.raylink.live')
        config.set('verify', 'biz', '68392')
        config.set('verify', 'accessId', 'FkphScmT0y41ULYidYgWosj')
    elif process ==3:
        config.set('server', 'host', 'pre.avica.link')
        config.set('sso', 'host', 'sso-pre.avica.link')
        config.set('web', 'host', 'console-pre.avica.link')
        config.set('verify', 'biz', '678')
        config.set('verify', 'accessId', 'fERTA0lRzOEYZVPUkHmkO9x')
    elif process ==4:
        config.set('server', 'host', 'api.avica.link')
        config.set('sso', 'host', 'sso-overseas.raylink.live')
        config.set('web', 'host', 'console.avica.link')
        config.set('verify', 'biz', '230520')
        config.set('verify', 'accessId', 'YDYx1tQrwKCedOx2emZ6NPn')
    else :
        print("异常退出")
        exit()
    # 保存修改后的INI文件
    with open(ini_file, 'w') as file:
        config.write(file)


def chiose():
    global process
    while True:
        process = int(input("请输入1-4数字,切换环境:"))
        if process <= 2:
            target_process_name = "RayLink.exe"
            find_directory(target_process_name)
            find_server(process_root_directory,process)
            break
        elif process > 2:
            target_process_name = "Avica.exe"
            find_directory(target_process_name)
            find_server(process_root_directory,process)
            break
        else :
            print("输入异常")

def main():
    print("1.raylink测试环境\n2.raylink生产环境\n3.Avica测试环境\n2.Avica生产环境")
    # chiose()
    while True:
        process = int(input("请输入1-4数字,切换环境:"))
        if process <= 2:
            target_process_name = "RayLink.exe"
            find_directory(target_process_name)
            find_server(process_root_directory,process)
            break
        elif process > 2:
            target_process_name = "Avica.exe"
            find_directory(target_process_name)
            find_server(process_root_directory,process)
            break
        else :
            print("输入异常")
    window2 = tkinter.Tk()
    window2.withdraw()
    top = tkinter.Toplevel(window2)
    top.title('置顶提示')
    top.attributes('-topmost', True)
    if process == 1:
        kill_process('RayLinkWatch')
        kill_process('Raylink')
        kill_process('RayLinkService')
        kill_process('Raylink.exe')
        kill_process('Raylink.exe')
        messagebox.showinfo('提示', 'Raylink测试环境切换成功!')
    elif process == 2:
        messagebox.showinfo('提示','Raylink生产环境切换成功')
    elif process == 3:
        messagebox.showinfo('提示','Avica测试环境切换成功')
    elif process == 4:
        messagebox.showinfo('提示','Avica生产环境切换成功')  
    else :
        print("异常退出")
        exit()
    window2.deiconify()

if __name__ == "__main__":
    run_as_admin()
    main()