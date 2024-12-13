from datetime import datetime
import logging
import time

# 配置日志记录器
logging.basicConfig(filename='./log/log_file.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
formatted_date_time=1
# 持续写入日志
while True:
    logging.info('{},  {}'.format(formatted_date_time, formatted_date_time))
    time.sleep(1) 