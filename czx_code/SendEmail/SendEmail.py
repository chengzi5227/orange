from datetime import datetime
import logging
import os
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


def send_email(status):
    
    with open(r'C:\Users\admin\Desktop\czx_py_test\SendEmail\file.txt', 'r' , encoding='utf-8') as file:
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

    # message = f'Hello, {username}! This is a custom message for you!'
    # message = f'<p>Dear all:</p><p>&nbsp;&nbsp;&nbsp;&nbsp;今日时间为{formatted_date_time},avica线上环境,PayPal真实账号支付金额0.1元，支付结果为：<span style="color:red;">{result}</span>!</p>'
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
            # "to": "zuowangwang@rayvision.com,wuweimin@rayvision.com,xiejinshi@rayvision.com,zhouhaiqi@rayvision.com,wangyanli@rayvision.com,angelachan@rayvision.com,angelachan@rayvision.com,zhoushuangquan@rayvision.com,chenzixin@rayvision.com",
            "subject": f"avica 每日支付验证-{result}",
            "HtmlBody": html_body,
            "MessageStream": "outbound"
            })
       )
    if json.loads(response.text)['ErrorCode'] ==0:
        print('邮件发送成功')
    else :
        print('邮件发送失败')
    return response

if __name__ == '__main__':
    response = send_email(True)
    print(response.text)
    # log('sendmail',response.text)
    log('sendmail',"1123123")
    print("niahsia1123")
    # with open(r'd:\nihao.txt', 'w', encoding='utf-8') as f:
    #     f.write("nihaio")



# import requests
# import json

# url = "https://api.postmarkapp.com/email"
# headers = {
#     "Accept": "application/json",
#     "Content-Type": "application/json",
#     "X-Postmark-Server-Token": "aa76442a-7206-4034-b44b-810bde1a9db7"
# }
# data = {
#     "From": "service3@avica.link",
#     "To": "chenzixin@rayvision.com",
#     "Subject": "Hello from Postmark",
#     "HtmlBody": "<strong>Hello</strong> dear Postmark user.",
#     "MessageStream": "outbound"
# }

# response = requests.post(url, headers=headers, data=json.dumps(data))

# # 打印响应内容
# print(response.text)