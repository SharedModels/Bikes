# -*- coding: utf-8 -*-
import requests as r
import pandas as pd
import json
import datetime
import time
from xml.etree.ElementTree import fromstring


class BikeScrape:
    def __init__(self, metadata="metadata.json", time_step=900.0):
        self.url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
        with open(metadata) as f:
            self.metadata = json.load(f)
        self.ids = [i for i in self.metadata.keys()]
        self.bikes_present = {}
        self.empty_docks = {}
        self.total_docks = {}
        self.bikes_presentDF = pd.DataFrame()
        self.empty_docksDF = pd.DataFrame()
        self.total_docksDF = pd.DataFrame()
        self.time_step = float(time_step)
        [self.initiate_dicts(i) for i in [self.bikes_present, self.empty_docks, self.total_docks]]

    def initiate_dicts(self, current_dict):
        for i in range(1000):
            current_dict[str(i)] = []
        current_dict['timestamp'] = []

    def scrape(self, maxrows, output_path):
        count = 0
        while True:
            timeNow = datetime.datetime.now()
            print("waiting")
            if (timeNow.minute in [0, 15, 30, 45]) & (timeNow.second == 0):
                break
        while count < maxrows:
            run_time = datetime.datetime.now()
            stamp = run_time.strftime("%Y-%m-%d %H:%M:%S")
            self.alternate_capture(stamp)
            count += 1
            self.create_dfs(output_path)
            print("run_time: " + stamp, self.time_step - (datetime.datetime.now() - run_time).total_seconds())
            if run_time.second > 0:
                time.sleep((self.time_step - run_time.second) - (datetime.datetime.now() - run_time).total_seconds())
            else:
                time.sleep(self.time_step - (datetime.datetime.now() - run_time).total_seconds())

        return self

    def capture(self, stamp):
        ping = r.get(self.url)
        content = fromstring(ping.content)
        print(content)
        current_present = []
        current_empty = []
        current_total = []
        print(content.find())
        for station in content.findall("station"):
            print(station)
            current_present.append(station.find("nbBikes").text)
            current_empty.append(station.find("nbEmptyDocks").text)
            current_total.append(station.find("nbDocks").text)

        checked_list = [i if len(i) == 839 else [0 for j in range(839)] for i in
                        [current_present, current_empty, current_total]]

        self.bikes_present[stamp] = checked_list[0].copy()
        self.empty_docks[stamp] = checked_list[1].copy()
        self.total_docks[stamp] = checked_list[2].copy()

    def dict_update(self, current_dict, ping_dict, stamp):
        for key, value in current_dict.items():
            try:
                value.append(ping_dict[key])
            except:
                if key == 'timestamp':
                    value.append(stamp)
                else:
                    value.append(0)

    def alternate_capture(self, stamp):
        ping = r.get(self.url)
        content = fromstring(ping.content)
        ping_bikes_dict = {}
        ping_empty_docks_dict = {}
        ping_docks_dict = {}
        for station in content.findall("station"):
            station_id = station.find('id').text
            ping_bikes_dict[station_id] = int(station.find("nbBikes").text)
            ping_empty_docks_dict[station_id] = int(station.find("nbEmptyDocks").text)
            ping_docks_dict[station_id] = int(station.find("nbDocks").text)

        self.dict_update(self.bikes_present, ping_bikes_dict, stamp)
        self.dict_update(self.empty_docks, ping_empty_docks_dict, stamp)
        self.dict_update(self.total_docks, ping_docks_dict, stamp)

    def create_dfs(self, path):
        self.bikes_presentDF = pd.DataFrame(self.bikes_present)
        self.empty_docksDF = pd.DataFrame(self.bikes_present)
        self.total_docksDF = pd.DataFrame(self.total_docks)
        self.write_to_csv(path)

    def write_to_csv(self, path):
        self.bikes_presentDF.to_csv(path + "bikes_present.csv")
        self.empty_docksDF.to_csv(path + "empty_docks.csv")
        self.total_docksDF.to_csv(path + "total_docks.csv")


if __name__ == '__main__':
    obj = BikeScrape(time_step=60)
    obj.scrape(100, 'lol')
