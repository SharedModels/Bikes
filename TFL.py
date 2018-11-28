# -*- coding: utf-8 -*-
import requests as r
import pandas as pd
import json
import datetime

from xml.etree.ElementTree import fromstring

class BikeScrape:
    def __init__(self, metadata="metadata.json"):
        self.url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        with open(metadata) as f:
            self.metadata = json.load(f)
        self.ids = [i for  i in self.metadata.keys()]
        self.ids.insert(0, 'Time')
        self.bikespresent = pd.DataFrame(columns=self.ids)
        self.emptydocks = pd.DataFrame(columns=self.ids)
        self.totaldocks = pd.DataFrame(columns=self.ids)
    
    def scrape(self):
        while True:
             time = datetime.datetime.now()
             stamp = time.strftime("%Y-%m-%d %H:%M:%S")
             if time.minute%15 == 0:
                 ping = r.get(self.url)
                 content = fromstring(ping.content)
                 present = [stamp]; empty = [stamp]; total = [stamp]
                 for station in content:
                     present.append(content[10])
                     empty.append(content[11])
                     total.append(content[12])
                 df1 = pd.DataFrame(present, columns=self.ids)
                 df2 = pd.DataFrame(empty, columns=self.ids)
                 df3 = pd.DataFrame(total, colums=self.ids)
                 self.bikespresent.append(df1)
                 self.emptydocks.append(df2)
                 self.totaldocks.append(df3)
  