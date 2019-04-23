from app import create_app, db
from app.models import Subscription, User, \
    Video, UserVideo, Search, FetchRecord, \
    Movie, Refe, Fetcher
from flask_script import Manager, Shell, Command
from flask_script.commands import ShowUrls
from flask_migrate import Migrate, MigrateCommand
import subprocess
import sys
import os


app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Subscription=Subscription,
                User=User, Video=Video, UserVideo=UserVideo,
                Search=Search, FetchRecord=FetchRecord, Movie=Movie,
                Refe=Refe, Fetcher=Fetcher)


class CeleryWorker(Command):
    name = 'celery'
    capture_all_args = True

    def run(self, argv):
        arg = argv[0]
        cmd1 = ['celery', 'beat', '-A', 'app.tasks.celery', '-S', 'redisbeat.RedisScheduler']
        cmd2 = ['celery', 'worker', '-A', 'app.tasks.celery', '-l', 'info']
        if arg == 'worker':
            cmd = cmd2
        elif arg == 'beat':
            cmd = cmd1
        ret = subprocess.call(cmd)
        sys.exit(ret)


@manager.command
def createdb():
    db.create_all()


@manager.command
def dropdb():
    db.drop_all()


@manager.command
def test():
    tests = subprocess.call(
        ['python', '-c', 'import tests; tests.run()']
    )
    sys.exit(tests)


@manager.command
def lint():
    lint = subprocess.call(
        ['flake8', '--ignore=E402', 'app/', 'manage.py', 'tests/']
    ) == 0
    if lint:
        print('OK')
    sys.exit(lint)


manager.add_command('showurl', ShowUrls)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('celery', CeleryWorker)


if __name__ == '__main__':
    if sys.argv[1] == 'test' or sys.argv[1] == 'lint':
        os.environ['KURA_CONFIG'] = 'testing'
    manager.run()
