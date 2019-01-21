import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import json


class BikesModelPipeline:
    def __init__(self, na_thresh=5):
        self.na_thresh = na_thresh

    @staticmethod
    def dock_positions():
        with open('metadata.json') as f:
            data = json.load(f)

        lat_position_dict = {}
        long_position_dict = {}

        for key, value in data.items():
            lat_position_dict[key] = value['Lat']
            long_position_dict[key] = value['Long']

        return lat_position_dict, long_position_dict

    def transform_to_rows(self, df):
        df = df.dropna(axis=1, thresh=self.na_thresh)

        df_rows = pd.melt(df, id_vars=["timestamp"],
                          var_name="dock", value_name="bikes_present")
        df_rows['dock'] = df_rows['dock'].astype(str)
        df_rows['timestamp'] = pd.to_datetime(df_rows['timestamp'])
        return df_rows

    def transform(self, df):
        lat_dock_pos, long_dock_pos = self.dock_positions()

        df['long'] = df['dock'].map(long_dock_pos)
        df['lat'] = df['dock'].map(lat_dock_pos)
        df = df.sort_values(['dock', 'timestamp'])
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 96, -1, -2]:
            df['bikes_present_{}'.format(i)] = df.groupby('dock').bikes_present.shift(i)

        df = df.dropna()
        df['hour'] = df.timestamp.dt.hour
        df['minute'] = df.timestamp.dt.minute
        return df

    def train_test_split(self, df, frac=0.3):
        df = self.transform_to_rows(df)
        df = self.transform(df)
        timestamp_unique = df.timestamp.unique()
        bottom_date = timestamp_unique[round((len(timestamp_unique) - len(timestamp_unique) * frac))]

        train = df[df['timestamp'] < pd.to_datetime(bottom_date)]
        test = df[df['timestamp'] >= pd.to_datetime(bottom_date)]
        return train, test


def fit_pred(train, test):
    clf = RandomForestRegressor()
    clf.fit(train.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2'], axis=1),
            train['bikes_present_-1'])
    test['pred'] = clf.predict(
        test.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2'], axis=1))

    test.to_csv('test_pred.csv')


if __name__ == '__main__':
    bikes_df = pd.read_csv('test7bikes_present.csv', index_col=0)
    bike_train, bike_test = BikesModelPipeline().train_test_split(bikes_df)
    fit_pred(bike_train, bike_test)

# print(df2.shape)
