import logging
import os
import subprocess
import sys
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import string
import requests
import json

#日志打印
def log(name,loginfo):
    log_dir = './log'
    log_file = os.path.join(log_dir, 'log_file.log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
    logging.info('{},{}'.format(name,loginfo))

#登录
# 测试环境
# username = "zuowangwang@rayvision.com"
# Apassword = "2edf692c26918cc7d11def6ab41bbdffdbecce52"
# email = "sb-fqj47926629610@personal.example.com"
# emailpassword = "0yG)$WBw"

# 生产环境
# 账号名RAY_chenzixin01
username = "chengzi5227@126.com"
Apassword = "0677fdd8d110c22b7bfa89d83dd8cd34ed2ed788"
email = "chengzitest@163.com"
emailpassword = "Ruiyun123"

def login():
    # 测试环境
    # url = "https://console-pre.avica.link/api/user/login/signIn"
    # 生产环境
    url = "https://console.avica.link/api/user/login/signIn"
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
        log('login',response.text)
    else :
        log('login',response.text)
        send_email(False)
        sys.exit()



#创建每日测试订阅订单
def dayPaypalSubscriptionTest():
    print (AUserkey)
    # 测试环境
    # url = "https://console-pre.avica.link/api/trade/subscription/dayPaypalSubscriptionTest"
    # 生产环境
    url = "https://console.avica.link/api/trade/subscription/dayPaypalSubscriptionTest"
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Userkey': AUserkey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

    if json.loads(response.text)['result'] == True :
        global AsubscriptionUrl
        AsubscriptionUrl = json.loads(response.text)['data']['subscriptionUrl']
        global AsubscriptionNo
        AsubscriptionNo = json.loads(response.text)['data']['subscriptionNo']
        print(AsubscriptionUrl)
        print(AsubscriptionNo)
        print("订单创建成功")
        log('dayPaypalSubscriptionTest',response.text)
        return AsubscriptionUrl,AsubscriptionNo
    else :
        log('dayPaypalSubscriptionTest',response.text)
        send_email(False)
        sys.exit()

    

#打开浏览器支付
def paypal():

    # 创建Chrome浏览器实例
    driver = webdriver.Chrome()
    print(AsubscriptionUrl)
    # 在浏览器中打开链接
    driver.get(AsubscriptionUrl)

    # 等待10秒
    time.sleep(10)

    # 输入邮箱
    email_input = driver.find_element(By.XPATH, '//*[@id="email"]')
    email_input.send_keys(email)

    driver.implicitly_wait(10)

    # 点击下一步
    next_button = driver.find_element(By.XPATH, '//*[@id="btnNext"]')
    next_button.click()

    # 等待10秒
    time.sleep(10)


    # 输入密码
    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(emailpassword)

    # 等待3秒
    time.sleep(3)

    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, '//*[@id="btnLogin"]')
    login_button.click()

    # 等待10秒
    time.sleep(10)


    # 点击同意按钮
    agree_button = driver.find_element(By.XPATH, '//*[@id="confirmButtonTop"]')
    agree_button.click()

    # 检查当前网址是否跳转到"avica"
    time.sleep(15)
    current_url = driver.current_url
    if "avica" in current_url:
        print("当前网址已跳转到avica")
        print('正常支付跳转')
        loginfo = "当前网址已跳转到avica,正常支付跳转"
        log('paypal',loginfo)
    else:
        print("当前网址未跳转到avica")
        print('支付未跳转')
        loginfo ="当前网址未跳转到avica,支付未跳转"
        log('paypal',loginfo)
        send_email(False)
        sys.exit()

    # 等待10秒
    time.sleep(10)

    # 关闭浏览器
    driver.quit()

#查询订单是否支付成功
def getpaypalstatus():

    # 等待20秒
    time.sleep(20)
    # 测试环境
    # url = "https://console-pre.avica.link/api/user/subscription/getSubscription?subscriptionNo="+AsubscriptionNo
    # 生产环境
    url = "https://console.avica.link/api/user/subscription/getSubscription?subscriptionNo="+AsubscriptionNo
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Userkey': AUserkey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    log('getpaypalstatus',response.text)
    status = json.loads(response.text)['data']['status']
    print (status)
    if  2 == status  :
        print('订单支付成功签约')
        log('getpaypalstatus',response.text)

    else:
        print('支付失败')
        log('getpaypalstatus',response.text)
        send_email(False)
        sys.exit()
    time.sleep(3)
    return(status)

#取消订单
def cancelpaypal():
    # 测试环境
    # url = "https://console-pre.avica.link/api/trade/subscription/cancel?subscriptionNo="+AsubscriptionNo
    # 生产环境
    url = "https://console.avica.link/api/trade/subscription/cancel?subscriptionNo="+AsubscriptionNo
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Userkey': AUserkey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    code = json.loads(response.text)['code']
    print(code)
    log('cancelpaypal',response.text)
    if  200 == code  :
        print('取消成功')
        log('cancelpaypal',response.text)
    else:
        print('取消失败')
        log('cancelpaypal',response.text)
        send_email(False)
        sys.exit()

    time.sleep(3)

#查询订单是否取消
def getcancelpaypalstatus():
    # 测试环境
    # url = "https://console-pre.avica.link/api/user/subscription/getSubscription?subscriptionNo="+AsubscriptionNo
    # 生产环境
    url = "https://console.avica.link/api/user/subscription/getSubscription?subscriptionNo="+AsubscriptionNo
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Userkey': AUserkey
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    status = json.loads(response.text)['data']['status']
    print(status)
    log('getcancelpaypalstatus',response.text)
    time.sleep(20)

    if  3 == status  :
        print('订阅取消成功')
        log('getcancelpaypalstatus',response.text)
        send_email(True)
    else:
        print('订阅取消失败')
        log('getcancelpaypalstatus',response.text)
        send_email(False)
        sys.exit()




# 发送邮件
def send_email(status):
    with open('file.txt', 'r' , encoding='utf-8') as file:
        html_template  = file.read()
    # status = 2
    if status ==True:
        result = '成功'
    else:
        result = '失败'
    date = datetime.now()
    formatted_date_time = date.strftime("%Y-%m-%d %H:%M")
    print(formatted_date_time)
    html_file = html_template.format(formatted_date_time=formatted_date_time,result=result)

    message = f'{html_file}'
    html_body = f'<strong>{message}</strong>'
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Postmark-Server-Token":"aa76442a-7206-4034-b44b-810bde1a9db7"
    }
    response = requests.post(
        "https://api.postmarkapp.com/email",
        headers=headers,
        data=json.dumps({
            "from": "service3@avica.link",
            "to":"chenzixin@rayvision.com",
            # "to": "zuowangwang@rayvision.com,wuweimin@rayvision.com,xiejinshi@rayvision.com,zhouhaiqi@rayvision.com,wangyanli@rayvision.com,gordon@rayvision.com,angelachan@rayvision.com,zhoushuangquan@rayvision.com,chenzixin@rayvision.com,chenzhenqun@rayvision.com,wanduanwei@rayvision.com",
            "subject": f"avica 每日支付验证-{result}",
            "HtmlBody": html_body,
            "MessageStream": "outbound"
            })
       )
    if json.loads(response.text)['ErrorCode'] ==0:
        print('邮件发送成功')
        log('send_email',response.text)
    else :
        print('邮件发送失败')
        log('send_email',response.text)
        sys.exit()
    

    return response




if __name__ == "__main__":
    try:
        login()
        dayPaypalSubscriptionTest()
        paypal()
        getpaypalstatus()
        cancelpaypal()
        getcancelpaypalstatus()
    except Exception as errorinfo:
        log('errorinfo',errorinfo)
        send_email(False)
    