### celery模块

celery是python开发的分布式任务调度模块，它本身不含消息服务，它使用第三方消息服务来传递任务，目前celery支持的消息服务有RabbitMQ，Redis甚至是数据库，淡然Redis是最好的选择

#### 架构组成

* 消息中间件（message broker）：

  Celery本身不提供消息服务，但是可以方便的和第三方提供的消息中间件集成（redis）。

* 任务执行单元（worker）：

  Worker是Celery提供的任务执行的单元，worker并发的运行在分布式的系统节点中。

* 任务结果存储（Task result store）：

  用来存储Worker执行的任务的结果，Celery支持以不同方式存储任务的结果，包括AMQP, Redis，memcached, MongoDB，SQLAlchemy, Django ORM，Apache Cassandra, IronCache

另外， Celery还支持不同的并发和序列化的手段

- 并发

  [Prefork](http://httpd.apache.org/docs/2.2/mod/prefork.html), [Eventlet](http://eventlet.net/), [gevent](http://gevent.org/), threads/single threaded

- 序列化

  pickle, json, yaml, msgpack. zlib, bzip2 compression， Cryptographic message signing 等等



#### 命令

```python
# 安装

pip install Celery
# 如果以redis作为broker的话需要如下安装
pip3 install celery-with-redis

# 编写worker
# 写任务单元，本次命名为tasks

# 启动celery服务（其中-A参数表示的是CeleryApp的名称），（在和worker同一目录下）
$ celery -A tasks worker --loglevel=info

# 发送邮件，执行任务，（在和worker同一目录下）
>>> from tasks import send_mail
>>> send_mail.delay('你好')
<AsyncResult: 70e9c346-99db-4042-88ce-df5c7fc51b99>
    
# 在worker里查看任务处理的消息
[2018-08-14 23:18:59,671: WARNING/Worker-1] sending mail to 你好
[2018-08-14 23:19:04,673: WARNING/Worker-1] mail send
[2018-08-14 23:19:04,675: INFO/MainProcess] Task tasks.send_mail[70e9c346-99db-4042-88ce-df5c7fc51b99] succeeded in 5.004449542997463s: None
```



### 项目中使用celery

```shell
# 项目目录
(venv) ➜  ~ mkdir celery_tasks
# celery的配置文件
(venv) ➜  ~ touch celery_tasks/celery.py
# 任务1
(venv) ➜  ~ touch celery_tasks/task_1.py
# 任务2
(venv) ➜  ~ touch celery_tasks/task_2.py
```

celery_tasks/celery.py

```python
from __future__ import absolute_import
from celery import Celery

app = Celery('celery_tasks',
             broker='redis://localhost',
             backend='redis://localhost',
             include=['celery_tasks.task_1', 'celery_tasks.task_2'])

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
```

celery_tasks/task_1.py

```python
from __future__ import absolute_import
from .celery import app


@app.task
def add(x, y):
    return x + y
```

celery_tasks/task_2.py

```python
from __future__ import absolute_import
import time
from .celery import app


@app.task
def sleep(t):
    time.sleep(t)
    return str(time.time())
```

启动

```shell
(venv) ➜  ~ celery -A celery_tasks worker -l info

celery@ShengdeMacBook-Pro.local v4.1.0 (latentcall)

Darwin-17.3.0-x86_64-i386-64bit 2018-01-22 14:59:33

[config]
.> app:         celery_tasks:0x109e29ef0
.> transport:   redis://localhost:6379//
.> results:     redis://localhost/
.> concurrency: 4 (prefork)
.> task events: OFF (enable -E to monitor tasks in this worker)

[queues]
.> celery           exchange=celery(direct) key=celery


[tasks]
  . celery_tasks.task_1.add
  . celery_tasks.task_2.sleep

[2018-01-22 14:59:34,042: INFO/MainProcess] Connected to redis://localhost:6379//
[2018-01-22 14:59:34,072: INFO/MainProcess] mingle: searching for neighbors
[2018-01-22 14:59:35,109: INFO/MainProcess] mingle: all alone
[2018-01-22 14:59:35,148: INFO/MainProcess] celery@ShengdeMacBook-Pro.local ready.
```

新开一个窗口测试

```shell
(venv) ➜  ~ python
>>> from celery_tasks import task_1,task_2
>>> task_1.add.delay(1,2)
<AsyncResult: 8621cc57-ddf1-4188-a21d-78678611c735>
>>> task_2.sleep.delay(5)
<AsyncResult: a842caa1-3162-460c-b49a-860797f7784b>
```

### 后台运行

启动

```python
(venv) ➜  ~ celery multi start celery_demo -A celery_tasks -l info
celery multi v4.1.0 (latentcall)
> Starting nodes...
    > celery_demo@ShengdeMacBook-Pro.local: OK
```

查看进程

```python
(venv) ➜  ~ ps -ef | grep celery_demo | grep -v grep
  501 30862     1   0  3:03下午 ??         0:00.72 /Users/shengan/.pyenv/versions/3.6.3/envs/venv/bin/python -m celery worker -A celery_tasks -l info --logfile=celery_demo%I.log --pidfile=celery_demo.pid --hostname=celery_demo@ShengdeMacBook-Pro.local
  501 30900 30862   0  3:03下午 ??         0:00.01 /Users/shengan/.pyenv/versions/3.6.3/envs/venv/bin/python -m celery worker -A celery_tasks -l info --logfile=celery_demo%I.log --pidfile=celery_demo.pid --hostname=celery_demo@ShengdeMacBook-Pro.local
  501 30901 30862   0  3:03下午 ??         0:00.01 /Users/shengan/.pyenv/versions/3.6.3/envs/venv/bin/python -m celery worker -A celery_tasks -l info --logfile=celery_demo%I.log --pidfile=celery_demo.pid --hostname=celery_demo@ShengdeMacBook-Pro.local
  501 30902 30862   0  3:03下午 ??         0:00.01 /Users/shengan/.pyenv/versions/3.6.3/envs/venv/bin/python -m celery worker -A celery_tasks -l info --logfile=celery_demo%I.log --pidfile=celery_demo.pid --hostname=celery_demo@ShengdeMacBook-Pro.local
  501 30903 30862   0  3:03下午 ??         0:00.01 /Users/shengan/.pyenv/versions/3.6.3/envs/venv/bin/python -m celery worker -A celery_tasks -l info --logfile=celery_demo%I.log --pidfile=celery_demo.pid --hostname=celery_demo@ShengdeMacBook-Pro.local
```

一个守护进程，`worker`个数等于`CPU`个数。

重启

```
(venv) ➜  ~ celery multi restart celery_demo -A celery_tasks -l info
celery multi v4.1.0 (latentcall)
> Stopping nodes...
    > celery_demo@ShengdeMacBook-Pro.local: TERM -> 31132
> Waiting for 1 node -> 31132.....
    > celery_demo@ShengdeMacBook-Pro.local: OK
> Restarting node celery_demo@ShengdeMacBook-Pro.local: OK
> Waiting for 1 node -> None...
```

停止

```
(venv) ➜  ~ celery multi stop celery_demo -A celery_tasks -l info
celery multi v4.1.0 (latentcall)
> Stopping nodes...
    > celery_demo@ShengdeMacBook-Pro.local: TERM -> 30862
```

等待任务执行完毕后停止

```
(venv) ➜  ~ celery multi stopwait celery_demo -A celery_tasks -l info
```

