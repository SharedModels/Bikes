# -*- coding: utf-8 -*-
import requests as r
import pandas as pd
import json
import datetime
import xml.etree.ElementTree as ET
import numpy as np

from xml.etree.ElementTree import fromstring

class BikeScrape:
    def __init__(self, metadata="metadata.json"):
        self.url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        with open(metadata) as f:
            self.metadata = json.load(f)
        self.ids = [i for i in self.metadata.keys()]
        # self.cols = ids.insert(0, 'Time')
        self.bikespresent = pd.DataFrame(columns=self.ids)
        self.emptydocks = pd.DataFrame(columns=self.ids)
        self.totaldocks = pd.DataFrame(columns=self.ids)
    
    def scrape(self, maxrows):
        count = 0
        startTime = datetime.datetime.now()
        while count < maxrows:
            runTime = datetime.datetime.now()
            timeDelta = runTime - startTime
            print(timeDelta.seconds)
            stamp = runTime.strftime("%Y-%m-%d %H:%M:%S")
            if timeDelta.seconds % 10 == 0:
                BikeScrape.capture(self, stamp)
                count += 1
            else:
                continue

    def capture(self, stamp):
        ping = r.get(self.url)
        content = fromstring(ping.content)
        present = []
        empty = []
        total = []
        for station in content.findall("station"):
            present.append(station.find("nbBikes").text)
            print(station.find("nbBikes").text)
            empty.append(station.find("nbEmptyDocks").text)
            total.append(station.find("nbDocks").text)
        df1 = pd.DataFrame(present, columns=self.ids)
        #df2 = pd.DataFrame(empty).transpose()  # , columns=self.ids)
        #df3 = pd.DataFrame(total).transpose()  # , columns=self.ids)
        self.bikespresent.append(df1)
        #self.emptydocks.append(df2)
        #self.totaldocks.append(df3)


