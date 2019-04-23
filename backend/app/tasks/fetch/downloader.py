# -*- coding: utf-8 -*-
from pyppeteer.launcher import connect
import asyncio


class Download:

    def __init__(self):
        self.browser = None
        self.page = None
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.get_browser())
        loop.run_until_complete(task)

    async def get_browser(self):
        self.browser = await connect({'browserWSEndpoint':
                                      'ws://127.0.0.1:9222/devtools/browser/b24506f9-501d-4885-b1db-5b187547aab3',
                                      'ignoreHTTPSErrors': True})
        self.page = await self.browser.newPage()

    async def get_page(self):
        return await self.browser.newPage()

    async def downloader(self, url):
        print('fetch from {}...'.format(url))
        await self.page.goto(url)
        content = await self.page.content()
        return content

    def run(self, url):
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.downloader(url))
        loop.run_until_complete(task)

        return task.result()


if __name__ == '__main__':
    d = Download()
    print(d.run('http://fjisu.com/search/jojo'))
