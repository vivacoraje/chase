# Chase

搜索你喜爱的电视剧，点击订阅，chase帮你收集剧集的播放地址和下载地址，更新时向你发来提醒邮件。[backend]()基于Python3.6，Flask，MySQL，Celery。[frontend]()基于vue，ant-design-vue

# 特性

- 前后端分离。

- 一部电视剧，对应一个订阅，对应一个定时任务。

- 针对电视剧的更新规律，调整定时任务的调度规则，电视剧完结后任务将被停止。
- 从四个不同网站（豆瓣电影，IMDB， ziziyy，loldytt）抓取关键信息。（其中loldytt容易崩溃和封锁IP，未实装）

# 运行

```
git clone
```

### client
(可省略)
```
cd client/kura
yarn install
yarn dev
```

### backend

在backend目录中创建.env
```
COMPOSE_PROJECT_NAME=chase
SECRET_KEY=top_secret
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_REDIS_SCHEDULER_URL=redis://redis:6379/3
SQLALCHEMY_DATABASE_URI=mysql+pymysql://chase:123456@mysql:3306/chase
MAIL_SERVER=*
MAIL_PORT=*
MAIL_USERNAME=*
MAIL_PASSWORD=*
MAIL_SUBJECT_PREFIX=[Chase]
CHASE_CONFIG=development
```

须安装Docker和docker-compose
```
cd backend
make docker
```

# 访问

- 本机
[localhost:5000](http://localhost:5000)
[localhost:808*](http://localhost:8080)(未省略`#client`)

- heroku
[chase](https://powerful-sands-58878.herokuapp.com/)
