from flask import current_app
from flask_mail import Message
from app.extensions import mail
from app.tasks import celery


mail_temp = '''
<div class="layout one-col fixed-width" style="Margin: 0 auto; max-with: 600px; min-width: 400px; width: 400px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all">
    <div class="layout__inner" style="border-collapse: collapse; display: table;width: 100%;background-color: #ffffff">
        <div class="column" style="text-align: left; color: #595959; font-size: 14px; line-height: 26px; font-family: Lato,Tahoma,sans-serif;max-width: 600px;min-width: 320px;width: 400px">
            <div style="Margin-left: 20px;Margin-right: 20px;margin-top: 20px;width: 370px">
                <p>阁下，您好：</p>
                <p>您用邮箱（{{ email }}）订阅的影片<a href="{{ tv_url }}">{{ tv_title }}</a>已更新。</p>
                {% for d_a, v_t in zip(download_address, video_title) %}
                <p><a href="{{ d_a }}">{{ v_t }}</a> {{ d_a }}</p>
                {% endfor %}
                <p><a href="">或者查看更多</a>。</p>
                <p>致辞<br><br>Kura Admin</p>
            </div>
        </div>
    </div>
</div>
'''


@celery.task
def send_email(to, subject, html):
    """发送邮件
    :param to: 向谁发送
    :param subject: 邮件主题
    :param html: 邮件模板
    """
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])

    msg.html = html

    mail.send(msg)
