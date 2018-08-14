import time
from celery import Celery

# 第一个参数是app的名称,broker指定接收和发送任务消息代理的url，backend指定存储任务执行结果的代理url
celery = Celery('tasks', broker='redis://localhost:6379', backend='redis://localhost:6379')


# 任务列表
@celery.task
def send_mail(mail):
    print('sending mail to %s' % mail)
    time.sleep(5)
    print('mail send')

