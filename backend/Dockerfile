# Grab the lastest alpine image
FROM alpine:latest

# Install python and pip
RUN echo http://mirrors.ustc.edu.cn/alpine/v3.7/main/ > /etc/apk/repositories; \
echo http://mirrors.ustc.edu.cn/alpine/v3.7/community/ >> /etc/apk/repositories
RUN apk add --no-cache python3 py3-pip bash py3-lxml py3-psycopg2
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --upgrade pip setuptools
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --no-cache-dir -q -r /tmp/requirements.txt

# Add code
ADD . /opt/chase/
WORKDIR /opt/chase

# EXPOSE 5000
RUN adduser -D myuser
RUN chown myuser:myuser /opt/chase
USER myuser

# Run the app
CMD gunicorn --bind 0.0.0.0:$PORT wsgi