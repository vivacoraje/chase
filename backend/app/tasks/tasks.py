from app.extensions import db
from app.models import Video, FetchRecord, Movie, Fetcher
from . import celery
from ..schedule import scheduler
from functools import partial
from .fetch import Movie as MovieInfo
from .fetch import AddressFetcher
from app.utils import domain
from app.utils import init_schedule
from celery import chain, group
from flask import render_template
from .send_email import send_email


address_fetcher = AddressFetcher()


@celery.task
def timed_crawl_address(tv_url):
    c = address_fetcher.fetch(tv_url)
    if c is None:
        return
    videos = c.episodes

    db.session.remove()

    fetcher = Fetcher.query.filter_by(url=tv_url).first()
    subs = fetcher.subscription
    users = subs.users
    addrs = {a for _, a in videos}
    old_videos = fetcher.videos
    old_addrs = {o.address for o in old_videos}
    new_addrs = addrs - old_addrs

    # 订阅任务未完成，却没有抓取到新的下载地址，调用Subscription.postponed_update()方法更新current_schedule
    if not fetcher.ended and not new_addrs:
        fetcher.postponed_update()

    fetch_record_create = partial(FetchRecord.create, schedule=str(scheduler.get_schedule(tv_url)))
    if new_addrs:
        fr = fetch_record_create(updated=True)
    else:
        fr = fetch_record_create()
    fetcher.fetch_records.append(fr)
    db.session.add(subs)

    new_videos = [Video(title=t, address=a) for t, a in videos if a in new_addrs]
    all_videos = new_videos + fetcher.videos.all()

    for user in users:
        videos = new_videos if user.videos.filter_by(subscription=subs).all() else all_videos
        for video in videos:
            user.add_video(video=video, fetcher=fetcher)
        if fr.updated and user.confirmed:
            send_email(user.email,
                       '影片更新提醒',
                       render_template('mail/push.html',
                                       tv_title=subs.movie.title,
                                       address_type=fetcher.address_type))
    db.session.commit()
    db.session.remove()

    fetcher = Fetcher.query.filter_by(url=tv_url).first()
    # 如果订阅任务下的视频下载地址数目大于或等于电视剧的集数，将定时任务从Redis中删除
    if fetcher.is_ended():
        scheduler.remove(tv_url)

        db.session.remove()
        subs = fetcher.subscription
        subs.ended = True
        db.session.add(subs)
        db.session.commit()
        return

    # 如果fetch_record数目大于`21`(即三周)
    if fetcher.should_adjust():
        scheduler.replace(tv_url, fetcher.schedule)
        db.session.add(fetcher)
        db.session.commit()


@celery.task
def first_fetch_address(tv_url):
    c = address_fetcher.fetch(tv_url)
    if c is None:
        return
    videos = c.episodes

    fetcher = Fetcher.query.filter_by(url=tv_url).first()
    fetcher.address_type = c.address_type
    db.session.add(fetcher)
    db.session.commit()

    subs = fetcher.subscription
    if fetcher:
        subs.fetchers.append(fetcher)

        videos = [Video(title=t, address=a) for t, a in videos]

        for u in subs.users:
            for video in videos:
                u.add_video(video, fetcher)
            if u.confirmed:
                send_email(u.email,
                           '影片更新提醒',
                           render_template('mail/push.html',
                                           tv_title=subs.movie.title,
                                           address_type=fetcher.address_type))
        db.session.commit()


@celery.task
def fetch_movie_info(movie_id, tv_url):
    """
        tv_url: '*.loldyttw.*'
    """
    m = Movie.query.filter_by(id=movie_id).first()
    c = address_fetcher.fetch(tv_url)
    if c is None:
        return
    title = c.title

    m.subscription.title = title

    fetcher = Fetcher.create(tv_url)
    fetcher.address_type = c.address_type
    m.subscription.fetchers.append(fetcher)
    videos = [Video(title=t, address=a) for t, a in c.episodes]

    for u in m.subscription.users:
        for video in videos:
            u.add_video(video, fetcher)
    db.session.add(m)
    db.session.commit()

    mi = MovieInfo(title)
    mi_dict = mi.to_dict()
    other_urls = mi.fetchable_urls()
    other_fetchers = [Fetcher.create(other) for other in other_urls]
    m.subscription.fetchers.extend(other_fetchers)

    mi_dict['refes'].update({domain(tv_url): {'url': tv_url, 'fetchable': True}})
    m.from_dict(mi_dict)

    db.session.add(m)
    db.session.commit()

    scheduler.add(**{
        'name': tv_url,
        'task': 'app.tasks.tasks.timed_crawl_address',
        'schedule': init_schedule(),
        'args': (tv_url, )
    })
    return other_urls


@celery.task
def fetch_group(urls):
    group(first_fetch_address.s(url) for url in urls)()


def fetch_chain(movie_id, tv_url):
    res = chain(fetch_movie_info.s(movie_id, tv_url), fetch_group.s())
    res()
