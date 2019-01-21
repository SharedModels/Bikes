import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import json


def dock_positions():
    with open('metadata.json') as f:
        data = json.load(f)

    lat_position_dict = {}
    long_position_dict = {}

    for key, value in data.items():
        lat_position_dict[key] = value['Lat']
        long_position_dict[key] = value['Long']

    return lat_position_dict, long_position_dict


df = pd.read_csv('test7bikes_present.csv', index_col=0)
df = df.dropna(axis=1)

"""Row for each timestamp, lat/long, previous n , previous 24 * 15"""

df2 = pd.melt(df, id_vars=["timestamp"],
              var_name="dock", value_name="bikes_present")
lat_dock_pos, long_dock_pos = dock_positions()
df2['dock'] = df2['dock'].astype(str)
df2['timestamp'] = pd.to_datetime(df2['timestamp'])

df2['long'] = df2['dock'].map(long_dock_pos)
df2['lat'] = df2['dock'].map(lat_dock_pos)
df2 = df2.sort_values(['dock', 'timestamp'])
for i in [1, 2, 3, 4, 5, 6, 7, 8, 96, -1, -2]:
    df2['bikes_present_{}'.format(i)] = df2.groupby('dock').bikes_present.shift(i)

df2 = df2.dropna()
df2['hour'] = df2.timestamp.dt.hour
df2['minute'] = df2.timestamp.dt.minute

timestamp_unique = df2.timestamp.unique()
bottom_date = timestamp_unique[round((len(timestamp_unique) - len(timestamp_unique) * 0.3))]

train = df2[df2['timestamp'] < pd.to_datetime(bottom_date)]
test = df2[df2['timestamp'] >= pd.to_datetime(bottom_date)]

clf = RandomForestRegressor()
clf.fit(train.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2'], axis=1),
        train['bikes_present_-1'])
test['pred'] = clf.predict(
    test.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2'], axis=1))

test.to_csv('test_pred.csv')
# print(df2.shape)
