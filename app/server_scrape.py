import pandas as pd
import numpy as np
import json
import requests as r
from xml.etree.ElementTree import fromstring
import datetime


class ServerScrape:
    def __init__(self, metadata='metadata.json'):
        self.url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        with open(metadata) as f:
            self.metadata = json.load(f)
        self.ids = [i for i in self.metadata.keys()]
        self.bikes_present = []
        self.empty_docks = []
        self.total_docks = []
        self.ping_bikes_present = {}
        self.ping_empty_docks = {}
        self.ping_total_docks = {}
        [self.initiate_dicts(i) for i in [self.ping_bikes_present, self.ping_empty_docks, self.ping_total_docks]]

    def initiate_dicts(self, current_dict):
        for i in range(1000):
            current_dict[str(i)] = np.nan
        current_dict['timestamp'] = np.nan

    def capture(self, timestamp):
        ping_bikes_dict = self.ping_bikes_present.copy()
        ping_empty_docks_dict = self.ping_empty_docks.copy()
        ping_docks_dict = self.ping_total_docks.copy()
        # Not sure if this is most efficient, need to test timings of this and just initiating each time
        try:
            ping = r.get(self.url)
            content = fromstring(ping.content)
            for station in content.findall("station"):
                station_id = station.find('id').text
                ping_bikes_dict[station_id] = int(station.find("nbBikes").text)
                ping_empty_docks_dict[station_id] = int(station.find("nbEmptyDocks").text)
                ping_docks_dict[station_id] = int(station.find("nbDocks").text)
        except Exception as e:
            print(e)
            pass
        for i in [ping_bikes_dict, ping_docks_dict, ping_empty_docks_dict]:
            i['timestamp'] = timestamp
        self.bikes_present.append(ping_bikes_dict)
        self.empty_docks.append(ping_empty_docks_dict)
        self.total_docks.append(ping_docks_dict)

    def update(self, number_keep):
        run_time = datetime.datetime.now()
        stamp = run_time.strftime("%Y-%m-%d %H:%M:%S")
        self.capture(stamp)
        if len(self.bikes_present) > number_keep:
            self.bikes_present = self.bikes_present[1:]
            self.empty_docks = self.empty_docks[1:]
            self.total_docks = self.total_docks[1:]
        return pd.DataFrame(self.bikes_present), pd.DataFrame(self.empty_docks), pd.DataFrame(self.total_docks)


if __name__ == '__main__':
    import time

    obj = ServerScrape('metadata.json')
    for j in range(1000):
        a, b, c = obj.update(150)
        print(a.shape)
        time.sleep(5)
