




import configparser
import json
import os
import requests


def login(username,Apassword,process):
    # 个人版\n1.raylink测试环境\n2.raylink生产环境\n3.Avica测试环境\n4.Avica生产环境
    if process == 1 :
        url = "https://console-pre.raylink.live/api/user/login/signIn"
    elif process == 2 :
        url = "https://console.raylink.live/api/user/login/signIn"
    elif process == 3 :
        url = "https://console-pre.avica.com/api/user/login/signIn"
    elif process == 4 :
        url = "https://console.avica.com/api/user/login/signIn"

    payload = json.dumps({
    "loginName": username,
    "password": Apassword,
    "loginPlatform": 1,
    "extendData": {
        "zone": 2
    },
    "osVersion": "Chrome120.0.0.0",
    "loginOs": 6,
    "deviceName": "Chrome",
    "macAddress": "04b0ac129149245ebbe3aee16f20dcce",
    "clientVersion": "v1.0.5"
    })
    headers = {
    'Content-Type': 'application/json',
    'Cookie': 'userKey=rsat:hDK8s55MbxcbTQhGHVWbJf26YvC'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
    if json.loads(response.text)['result'] == True :
        global AUserkey 
        AUserkey = json.loads(response.text)['data']['rsAuthToken']
        print (AUserkey)
        print("用户登录成功")
        if process == 1 or process == 2 :
            directory = '%%appdata%%\RayLink'
            filename = "client_config.json"
            ini_file = os.path.join(directory, filename)
            #修改访问权限
            os.chmod(ini_file, 0o666)
            # 创建ConfigParser对象并读取INI文件内容
            config = configparser.ConfigParser()
            config.read(ini_file)
            config.set('last_login_token', AUserkey)



        elif process == 3 or process == 4 :
            url = "https://console.raylink.live/api/user/login/signIn"
            # %appdta%\RayLink\client_config.json
    else :
        print("用户登录失败")





def main():
    process = int(input("请输入1-4数字,录入不同环境账号密码:"))
    print("个人版\n1.raylink测试环境\n2.raylink生产环境\n3.Avica测试环境\n4.Avica生产环境\n")
    username = str(input("请输入账号:"))
    password = str(input("请输入密码:"))
    login(username,password,process)


if __name__ == "__main__":
    main()