import pandas as pd
import numpy as np
import json
import requests as r
from xml.etree.ElementTree import fromstring
import datetime
import time
import app.config


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


class ConstantScrape:
    def __init__(self, db_engine=None, interval_time=15 * 60, scraper=ServerScrape()):
        self.interval_time = interval_time
        self.scraper = scraper
        if db_engine is None:
            path = os.path.join('mysql+pymysql://' + app.config.MYSQL_USERNAME + ':' + app.config.MYSQL_PASSWORD +
                                '@bikes-db-1.cxd403f5i8vi.eu-west-2.rds.amazonaws.com:3306/bikes')
            self.db_engine = create_engine(path)
        else:
            self.db_engine = db_engine
        # HACK HACK HACK HACK
        self.bikes_keep_columns = list(pd.read_sql_query("SELECT * FROM bikes.bikes_present", self.db_engine))
        self.empty_keep_columns = list(pd.read_sql_query("SELECT * FROM bikes.empty_docks", self.db_engine))
        self.total_keep_columns = list(pd.read_sql_query("SELECT * FROM bikes.total_docks", self.db_engine))
        # self.keep_columns.remove('index')

    def single_scrape(self):
        bikes_present, empty_docks, total_docks = self.scraper.update(1)
        bikes_present[self.bikes_keep_columns].to_sql('bikes_present', self.db_engine, if_exists='append', index=False)
        empty_docks[self.empty_keep_columns].to_sql('empty_docks', self.db_engine, if_exists='append', index=False)
        total_docks[self.total_keep_columns].to_sql('total_docks', self.db_engine, if_exists='append', index=False)

    def constant_scrape(self):
        while datetime.datetime.now().minute not in (15, 30, 45, 0):
            print('waiting to start')
            continue
        while True:
            start_time = datetime.datetime.now()
            print(start_time)
            self.single_scrape()
            final_time = self.interval_time - ((datetime.datetime.now() - start_time).seconds + start_time.second)
            time.sleep(final_time)


if __name__ == '__main__':
    import os
    from sqlalchemy import create_engine

    path = os.path.join('mysql+pymysql://' + app.config.MYSQL_USERNAME + ':' + app.config.MYSQL_PASSWORD +
                        '@bikes-db-1.cxd403f5i8vi.eu-west-2.rds.amazonaws.com:3306/bikes')
    engine = create_engine(path)

    ConstantScrape(engine).constant_scrape()
