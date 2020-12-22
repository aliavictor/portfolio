"""
This was a recent 2 hour exercise I did for another company. It presented an interesting
challenge and I had a lot of fun working through it, so I decided to include it.

For reference, I was given a normalized JSON file of RSS feed data from a slew of
articles across the web. The JSON may have been normalized, but just barely so; it was
still pretty messy in that not everything contained the same keys/information. The
challenge was as follows:

1. Determine which artist(s) each article is about
2. Match each artist to their corresponding database IDs using the company's public API
3. Return a JSON of this mapping
"""

import asyncio, aiohttp
import nest_asyncio
import spacy
import json
from json import JSONDecodeError
import re
import pandas as pd
nlp = spacy.load('en_core_web_sm')
nest_asyncio.apply()

# misc little helper functions
def strip_html(txt):
    return re.sub("<.*?>", "", txt)
def parse_ents(nlp_txt):
    return [d.text for d in nlp_txt.ents if d.label_ == 'PERSON']
def unique(obj):
    """Returns a list or Pandas Series after ensuring there are unique values"""
    if type(obj) == pd.Series:
        out = list(obj.unique())
    else:
        out_temp = set()
        out_add = out_temp.add
        out = [x for x in obj.copy() if not (x in out_temp or out_add(x))]
    return out
def empty(obj):
    """Return True if obj is either null, blank or len(obj) == 0"""
    if obj is None:
        return True
    elif type(obj) in (pd.DataFrame,pd.Series):
        if len(list(obj.columns)) > 1:
            return bool(len(obj)==0 or (obj[list(obj.columns)[0]].values[0] == '' and
                                        obj[list(obj.columns)[1]].values[0] == ''))
        else:
            return bool(len(obj)==0 or obj[list(obj.columns)[0]].values[0] == '')
    elif type(obj) == list:
        return bool(obj == [])
    elif type(obj) == str:
        return bool(obj == '')
    elif type(obj) == dict:
        return bool(len(keys(obj))==0)

rawdata = json.load(open('rss_feed.json'))

# identify as many artists as possible
# keep track of articles where no artist data can be found for later inspection
artist_map = {}
missed = []
for k,v in rawdata.items():
    if 'tags' not in v:
        missed.append(k)
        continue
    tags = [i['term'] for i in v['tags']]
    # parse entity labels of article tags via spacy's nlp feature
    tag_ents = [nlp(t).ents for t in tags]
    # create map of entities with corresponding list index
    ent_map = {ix:d[0].label_ for ix,d in enumerate(tag_ents) if len(d) > 0}
    # if any entities are labeled as a person, assume those are artist names
    if any(v == 'PERSON' for k,v in ent_map.items()):
        artist_map[k] = unique([tags[i] for i in [k for k,v in ent_map.items() if v == 'PERSON']])
    # if there's a non-empty content key attempt to find artists through the content value
    elif 'content' in v and any('value' in i for i in v['content']):
        raw_art_cont = v['content'][0]['value']
        art_cont = nlp(strip_html(raw_art_cont))
        if any(d.label_ == 'PERSON' for d in art_cont.ents):
            found_names = parse_ents(art_cont)
            # want to avoid cases where nlp incorrectly labels an entity as a person
            # so if some of the items in found_names have more than one word, take those
            if any(len(i.split())>1 for i in found_names):
                artist_map[k] = unique([i for i in found_names if len(i.split()) > 1])
            # otherwise if all found_names are only 1 word jst take them all
            else:
                artist_map[k] = unique(found_names)
        # if no entities labeled as a person are found in content, try summary/summary_detail keys
        else:
            summ = nlp(v['summary'])
            summ_det = nlp(v['summary_detail']['value'])
            if any(d.label_ == 'PERSON' for d in summ.ents):
                found_names = [d.text for d in summ.ents if d.label_ == 'PERSON']
                artist_map[k] = unique(found_names)
            elif any(d.label_ == 'PERSON' for d in summ_det.ents):
                found_names = [d.text for d in summ_det.ents if d.label_ == 'PERSON']
                artist_map[k] = unique(found_names)
    # if tags and content keys are a bust, next try summary/summary_detail keys
    else:
        summ = nlp(v['summary'])
        summ_det = nlp(v['summary_detail']['value'])
        if any(d.label_ == 'PERSON' for d in summ.ents):
            found_names = [d.text for d in summ.ents if d.label_ == 'PERSON']
            artist_map[k] = unique(found_names)
        # if summary key also yields no artists, try summary_detail key
        elif any(d.label_ == 'PERSON' for d in summ_det.ents):
            found_names = [d.text for d in summ_det.ents if d.label_ == 'PERSON']
            artist_map[k] = unique(found_names)
        # if none of these keys yield results, add to missed and inspect later
        else:
            missed.append(k)

# create api search urls for every artist name found
def api_search(x):
    url = 'https://beta-api.company.com/v1/artists?search={0}&thresh=0.3' # placeholder api url
    search_term = '+'.join([i.lower().strip() for i in x.split()])
    return url.format(search_term)
# create mapping of api search urls back to original rawdata key
search_urls = {api_search(i):k for k,v in artist_map.items() for i in v}

# asyncronously call all search requests and store results
async def fetch_all(urls):
    tasks = []
    async with aiohttp.ClientSession(loop=loop) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url,session))
            tasks.append(task)
        ans = await asyncio.gather(*tasks)
        return ans
async def fetch(url,session):
    async with session.get(url) as response:
        raw_data = []
        try:
            resp = json.loads(await response.read())
        except JSONDecodeError:
            return {'url':url,'resp':None}
        if 'error' not in resp:
            raw_data += resp['data'] if 'data' in resp else [resp]
        tries = 0
        while 'error' in resp:
            tries += 1
            await asyncio.sleep(3)
            resp = json.loads(await response.read())
            raw_data += resp['data'] if 'data' in resp else [resp]
            if tries == 3:
                break
        if 'paging' in resp:
            while 'next' in resp['paging']:
                async with session.get(resp['paging']['next']) as response:
                    resp = json.loads(await response.read())
                    if 'error' not in resp:
                        raw_data += resp['data'] if 'data' in resp else [resp]
                    tries = 0
                    while 'error' in resp:
                        tries += 1
                        await asyncio.sleep(3)
                        resp = json.loads(await response.read())
                        raw_data += resp['data'] if 'data' in resp else [resp]
                        if tries == 3:
                            break
                    if 'paging' not in resp:
                        break
        out = {}
        out['url'] = url
        out['resp'] = raw_data
        return out
raw_results = []
try:
    loop = asyncio.get_event_loop()
except RuntimeError: # if there's no existing loop, make one
    loop = asyncio.new_event_loop()
future = asyncio.ensure_future(fetch_all([k for k,v in search_urls.items()]))
x = loop.run_until_complete(future)
raw_results.extend(x)
# flatten results into easily accessible dict
results = {i['url']:[j for k in i['resp'] for j in k] for i in raw_results if i['resp']}
# map all found names to their ids
name_ids = {i['name']:i['id'] for k,v in results.items() for i in v if 'name' in i}

# create final mapping
final_map = {}
not_in_db = []
for k,v in artist_map.items():
    artists = []
    for name in v:
        if name in name_ids:
            artists.append({'name':name,'id':name_ids[name]})
        else:
            not_in_db.append(name)
    if not empty(artists):
        final_map[k] = artists