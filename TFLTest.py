from TFL import BikeScrape
import requests as r
import pandas as pd
import json
import datetime
import xml.etree.ElementTree as ET

bs = BikeScrape()
bs.capture(datetime.datetime.now)
bs.capture(datetime.datetime.now)


# url = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
# ping = r.get(url)
#
# content = ET.fromstring(ping.content)
#
# nBikesList =[]
# for station in content.findall("station"):
#     print(station.find("nbBikes").text)
#     nBikesList.append(station.find("nbBikes").text)
# df = pd.DataFrame(nBikesList).transpose
