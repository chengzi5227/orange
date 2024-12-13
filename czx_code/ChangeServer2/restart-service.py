import ctypes
import subprocess
import sys
from time import time
import win32service
import  os


# # 授权管理员
def run_as_admin():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise ctypes.WinError()
    except:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def test():
    try:
        os.system('NET STOP RayLinkService')
    except OSError:
        print('system error')
    os.system('NET START RayLinkService')


# 使用示例
def main():
    run_as_admin()
    # list_all_services()
    test1 = 'RayLinkService'
    test()


if __name__ == "__main__":
    main()