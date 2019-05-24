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


if __name__ == '__main__':
    print('spoopy')
