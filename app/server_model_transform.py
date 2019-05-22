import pandas as pd
import json


class BikesModelTransform:
    def __init__(self, na_thresh=5):
        self.na_thresh = na_thresh
        self.lat_dock_pos, self.long_dock_pos = self.dock_positions()

    def dock_positions(self):
        with open('metadata.json') as f:
            data = json.load(f)

        lat_position_dict = {}
        long_position_dict = {}

        for key, value in data.items():
            lat_position_dict[key] = value['Lat']
            long_position_dict[key] = value['Long']

        return lat_position_dict, long_position_dict,  # geohash

    def transform_to_rows(self, df, value_column):
        df = df.dropna(axis=1, thresh=self.na_thresh)

        df_rows = pd.melt(df, id_vars=["timestamp"],
                          var_name="dock", value_name=value_column)
        df_rows['dock'] = df_rows['dock'].astype(str)
        df_rows['timestamp'] = pd.to_datetime(df_rows['timestamp'])
        return df_rows

    def transform_to_train(self, df, value_column, loop_list=None, future=True):
        if not loop_list:
            loop_list = [i for i in range(10)] + ([-1, -2, -3, -4] if future else [])

        time_between = loop_list[2] - loop_list[1]
        df['long'] = df['dock'].map(self.long_dock_pos)
        df['lat'] = df['dock'].map(self.lat_dock_pos)
        df = df.sort_values(['dock', 'timestamp'])
        dock_groupby = df.groupby('dock')
        for i in loop_list:
            df[f'{value_column}_{int(i/time_between)}'] = dock_groupby[value_column].shift(i)

        df = df.dropna(thresh=self.na_thresh)
        df = df.dropna(axis=0)
        df['hour'] = df.timestamp.dt.hour
        df['minute'] = df.timestamp.dt.minute
        df['day'] = df.timestamp.dt.weekday
        return df

    def transform(self, df, value_column='bikes_present', loop_list=None, future=True):
        row_transformed = self.transform_to_rows(df, value_column)
        train_transform = self.transform_to_train(row_transformed, value_column, loop_list, future)
        return train_transform


#
#     def train_test_split(self, df, frac=0.2):
#         df['timestamp'] = pd.to_datetime(df['timestamp'])
#         df = df.sort_values('timestamp')
#         timestamp_unique = df.timestamp.unique()
#         bottom_date = timestamp_unique[round((len(timestamp_unique) - len(timestamp_unique) * frac))]
#         # df = self.transform(df)
#         train = df[df['timestamp'] < pd.to_datetime(bottom_date)]
#         test = df[df['timestamp'] >= pd.to_datetime(bottom_date)]
#         return train, test
#
#     def create_empty_docks(self, bikes_df, total_df):
#         bikes_df = bikes_df[bikes_df['timestamp'].isin(total_df.timestamp.unique())]
#         total_df = total_df[total_df['timestamp'].isin(bikes_df.timestamp.unique())]
#
#         empty_df = pd.DataFrame(total_df.drop('timestamp', axis=1).values - bikes_df.drop('timestamp', axis=1).values,
#                                 columns=list(bikes_df.drop('timestamp', axis=1)))
#         empty_df['timestamp'] = bikes_df.timestamp
#         empty_df = empty_df.sort_values('timestamp')
#         return empty_df
#
#
# class BikesClassificationPipeline(BikesModelPipeline):
#     def create_empty_column(self, df, number, value_column):
#         df[f'{value_column}_empty_-{number}'] = 0
#         df.loc[(df[f'{value_column}_-{number}'] == 0), f'{value_column}_empty_-{number}'] = 1
#         return df
#
#     def empty_dock_flag(self, df, value_column):
#         df[f'{value_column}_empty'] = 0
#         df.loc[(df[f'{value_column}'] == 0), f'{value_column}_empty'] = 1
#         for i in range(1, 5):
#             df = self.create_empty_column(df, i, value_column)
#         return df
#
#     def balance_classes(self, df, balance_column):
#         empty_bikes = df[(df[balance_column] == 1) & (df[balance_column] != 0)]
#         random_bikes = df[(df[balance_column] == 0)].sample(len(empty_bikes))
#         train_full = pd.concat([empty_bikes, random_bikes])
#         return train_full
#
#     def transform(self, df, value_column='bikes_present', loop_list=None, future=True):
#         row_transformed = self.transform_to_rows(df, value_column)
#         train_transform = self.transform_to_train(row_transformed, value_column, loop_list, future)
#         if future:
#             empty_dock = self.empty_dock_flag(train_transform, value_column)
#         else:
#             empty_dock = train_transform
#         return empty_dock
#
#     def train_test_pipeline(self, df, value_column='bikes_present'):
#         df = self.transform(df, value_column)
#         balanced_df = self.balance_classes(df, value_column)
#         train, test = self.train_test_split(balanced_df)
#         return train, test


if __name__ == '__main__':
    from server_scrape import ServerScrape
    import time

    obj = ServerScrape('metadata.json')
    transform = BikesModelTransform()
    while True:
        time.sleep(1)
        a, b, c = obj.update(20)
        print(a.shape)
        if len(a) < 19:
            continue
        d = transform.transform(a)
        print(d)
