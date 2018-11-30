# -*- coding: utf-8 -*-
import requests as r
import pandas as pd
import json
import datetime
import time
import xml.etree.ElementTree as ET
import numpy as np

from xml.etree.ElementTree import fromstring


class BikeScrape:
    def __init__(self, metadata="metadata.json"):
        self.url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        with open(metadata) as f:
            self.metadata = json.load(f)
        self.ids = [i for i in self.metadata.keys()]
        self.bikes_present = {}
        self.empty_docks = {}
        self.total_docks = {}
        # self.cols = ids.insert(0, 'Time')
        # self.bikespresent = pd.DataFrame(columns=self.ids)
        # self.emptydocks = pd.DataFrame(columns=self.ids)
        # self.totaldocks = pd.DataFrame(columns=self.ids)

    def scrape(self, maxrows):
        count = 0
        startTime = datetime.datetime.now()
        while count < maxrows:
            runTime = datetime.datetime.now()
            stamp = runTime.strftime("%Y-%m-%d %H:%M:%S")
            BikeScrape.capture(self, stamp)
            count += 1
            time.sleep(60 * 15)

        return self

    def capture(self, stamp):
        ping = r.get(self.url)
        content = fromstring(ping.content)
        current_present = []
        current_empty = []
        current_total = []
        for station in content.findall("station"):
            current_present.append(station.find("nbBikes").text)
            current_empty.append(station.find("nbEmptyDocks").text)
            current_total.append(station.find("nbDocks").text)

        self.bikes_present[stamp] = (current_present.copy())
        self.empty_docks[stamp] = (current_empty.copy())
        self.total_docks[stamp] = (current_total.copy())


a = BikeScrape().scrape(100)
print(a.bikes_present)