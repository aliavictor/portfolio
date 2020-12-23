from alia_toolbox.helpers import *
from alia_toolbox.colors import *
from sqlalchemy import create_engine
import pandas as pd
import difflib
import requests
from bs4 import BeautifulSoup

class Bleach(object):
    def __init__(self):
        self.engine = create_engine('sqlite:///bleach.db')
        self.epdata = pd.read_sql_query("select * from episodes;", self.engine)
        self.chpdata = pd.read_sql_query("select * from chapters;", self.engine)
        self.characters = Bleach.character_list()
    @staticmethod
    def character_list():
        cbase = 'https://bleach.fandom.com/wiki/Characters'
        chr_types = ['Shinigami','Arrancar','Hollow','Quincy','Humans','Souls','Miscellaneous']
        clinks = [f'{cbase}/{x}' for x in ['']+chr_types]
        characters = []
        for l in clinks:
            page = requests.get(l).content
            soup = BeautifulSoup(page,'html.parser')
            characters.extend([i.text for i in soup.find_all({'font':'color'}) if i.text not in chr_types])
        out = sorted([i.strip() for i in unique(characters)])
        return [i.replace('ō','ou').replace('Ō','O').replace('ū','uu') for i in out]
    def parse_character(self,x):
        if 'urahara' in x.lower() or 'kisuke' in x.lower():
            return 'Kisuke Urahara'
        elif 'rukia' in x.lower():
            return 'Rukia Kuchiki'
        elif 'byakuya' in x.lower():
            return 'Byakuya Kuchiki'
        elif 'grimm' in x.lower():
            return 'Grimmjow Jaegerjaquez'
        elif 'ichigo' in x.lower():
            return 'Ichigo Kurosaki'
        elif 'shinji' in x.lower():
            return 'Shinji Hirako'
        elif 'aizen' in x.lower():
            return 'Sousuke Aizen'
        elif 'stark' in x.lower():
            return 'Coyote Starrk'
        elif 'kensei' in x.lower():
            return 'Kensei Muguruma'
        elif 'renji' in x.lower():
            return 'Renji Abarai'
        elif 'hisagi' in x.lower():
            return 'Shuuhei Hisagi'
        elif 'yoruichi' in x.lower():
            return 'Yoruichi Shihouin'
        elif 'mashiro' in x.lower():
            return 'Mashiro Kuna'
        elif 'ururu' in x.lower():
            return 'Ururu Tsumugiya'
        elif 'jinta' in x.lower():
            return 'Jinta Hanakari'
        elif 'tessai' in x.lower():
            return 'Tessai Tsukabishi'
        else:
            return match(character,self.characters,hush=True)
    def find_episodes(self,character,sort=False):
        if not hasattr(self,'character'):
            chr_check = self.parse_character(character)
            if chr_check is None:
                red(f"<b>Can't find {character}</b>",False)
                return None
            else:
                self.character = chr_check
        if not hasattr(self,'character2'):
            self.character2 = ' '.join(self.character.split(" ")[::-1])

        mask = self.epdata['characters'].apply(
            lambda x: any(i in x.split('\n') for i in [self.character,self.character2]))
        self.episodes = self.epdata.loc[mask].reset_index(drop=True)
        self.episodes['mentions'] = 0
        self.episodes['relevant'] = 0

        cc = [c for c in [self.character,self.character2]+self.character.split()]
        cc = sorted(cc+[f"{i}'s" for i in cc],key=len,reverse=True)
        for row in self.episodes.itertuples():
            mentions = []
            for c in cc:
                mentions.append(row.summary.lower().count(c.lower()))
            self.episodes.loc[row.Index,'mentions'] = sum(mentions)
            relevant = [t for t in row.summary.split('\n') if any(f in t.lower() for f in self.character.lower().split(' '))]
            self.episodes.loc[row.Index,'relevant'] = '\n'.join(relevant)
        if sort:
            self.episodes = self.episodes.sort_values('mentions',ascending=False).reset_index(drop=True)
        return self.episodes
    def find_chapters(self,character,sort=False):
        if not hasattr(self,'character'):
            chr_check = self.parse_character(character)
            if chr_check is None:
                red(f"<b>Can't find {character}</b>",False)
                return None
            else:
                self.character = chr_check
        if not hasattr(self,'character2'):
            self.character2 = ' '.join(self.character.split(" ")[::-1])

        mask = self.chpdata['characters'].apply(
            lambda x: any(i in x.split('\n') for i in [self.character,self.character2]))
        self.chapters = self.chpdata.loc[mask].reset_index(drop=True)
        self.chapters['mentions'] = 0
        self.chapters['relevant'] = 0

        cc = [c for c in [self.character,self.character2]+self.character.split()]
        cc = sorted(cc+[f"{i}'s" for i in cc],key=len,reverse=True)
        for row in self.chapters.itertuples():
            mentions = []
            for c in cc:
                mentions.append(row.summary.lower().count(c.lower()))
            self.chapters.loc[row.Index,'mentions'] = sum(mentions)
            relevant = [t for t in row.summary.split('\n') if any(f in t.lower() for f in self.character.lower().split(' '))]
            self.chapters.loc[row.Index,'relevant'] = '\n'.join(relevant)
        if sort:
            self.chapters = self.chapters.sort_values('mentions',ascending=False).reset_index(drop=True)
        return self.chapters