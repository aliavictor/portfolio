import asyncio, nest_asyncio, aiohttp, requests
import functools as ft
from datetime import datetime
nest_asyncio.apply()

class FACEBOOK(object):
    def __init__(self,access_token,api_version='v8.0'):
        self.token = access_token
        self.api_v = api_version
        self.errors = []
    def read(self,obj_id,edge=None,fields=None,only_url=False,**params):
        """Reads an FB object (if the object is an ad account you must include act_ prefix). Params could be breakdowns='device_platform', etc. When only_url=True the compiled graph API url is returned."""
        if edge is None:
            base = f'https://graph.facebook.com/{self.api_v}/{obj_id}/?'
        else:
            base = f'https://graph.facebook.com/{self.api_v}/{obj_id}/{edge}/?'
        if fields is not None:
            if type(fields) != list:
                fields = fields.split(',')
        if params is not None:
            temp = []
            for key,val in params.items():
                temp.append(f'{key}={val}')
            params = '&'.join(temp)
        if fields and params:
            criteria = f'fields={",".join(fields)}&{params}'
        elif fields:
            criteria = f'fields={",".join(fields)}'
        elif params:
            criteria = f'{params}'
        else:
            criteria = ''
        self.read_url = f'{base}{criteria}&access_token={self.token}'
        if not only_url:
            return requests.get(self.read_url).json()
        else:
            return self.read_url
    def bulk_read(self,ids,edge=None,fields=None,**params):
        async def fetch_all(urls):
            tasks = []
            async with aiohttp.ClientSession(loop=self.loop) as session:
                for url in urls:
                    task = asyncio.ensure_future(fetch(url,session))
                    tasks.append(task)
                ans = await asyncio.gather(*tasks)
                return ans
        async def fetch(url,session):
            async with session.get(url) as self.response:
                self.raw_data = []
                resp = json.loads(await self.response.read())
                if 'error' not in resp:
                    self.raw_data += resp['data'] if 'data' in resp else [resp]
                tries = 0
                while 'error' in resp:
                    tries += 1
                    await asyncio.sleep(3)
                    resp = json.loads(await response.read())
                    self.raw_data += resp['data'] if 'data' in resp else [resp]
                    if tries == 3:
                        break
                if 'paging' in resp:
                    while 'next' in resp['paging']:
                        async with session.get(resp['paging']['next']) as self.response:
                            resp = json.loads(await self.response.read())
                            if 'error' not in resp:
                                self.raw_data += resp['data'] if 'data' in resp else [resp]
                            tries = 0
                            while 'error' in resp:
                                tries += 1
                                await asyncio.sleep(3)
                                resp = json.loads(await response.read())
                                self.raw_data += resp['data'] if 'data' in resp else [resp]
                                if tries == 3:
                                    break
                            if 'paging' not in resp:
                                break
                out = {}
                out['url'] = url
                out['resp'] = self.raw_data
                return out
        self.urls = list(map(ft.partial(self.read,edge=edge,fields=fields,only_url=True,**params),ids))
        print('Starting async pull [{0}]'.format(datetime.now().strftime('%m/%d/%y %H:%M:%S')))
        self.results = []
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError: # if there's no existing loop, make one
            self.loop = asyncio.new_event_loop()
        future = asyncio.ensure_future(fetch_all(self.urls))
        x = self.loop.run_until_complete(future)
        self.results.extend(x)
        return self.results