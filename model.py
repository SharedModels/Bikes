import pandas as pd
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
import json
from nn_class import SimpleNN


# import Geohash


class BikesModelPipeline:
    def __init__(self, na_thresh=5):
        self.na_thresh = na_thresh

    def combine_csvs(self, numbers=None, csv_name='bikes_present'):
        if numbers is None:
            numbers = [7, 8]
        csvs = []
        for i in numbers:
            try:
                csvs.append(pd.read_csv(f'test{i}{csv_name}.csv', index_col=0))
            except:
                continue
        return pd.concat(csvs, axis=0)

    def dock_positions(self):
        with open('metadata.json') as f:
            data = json.load(f)

        lat_position_dict = {}
        long_position_dict = {}
        geohash = {}

        for key, value in data.items():
            lat_position_dict[key] = value['Lat']
            long_position_dict[key] = value['Long']
            # geohash[key] = Geohash.encode(value['Lat'], value['Long'], precision=6)

        return lat_position_dict, long_position_dict,  # geohash

    def transform_to_rows(self, df, value_column):
        df = df.dropna(axis=1, thresh=self.na_thresh)

        df_rows = pd.melt(df, id_vars=["timestamp"],
                          var_name="dock", value_name=value_column)
        df_rows['dock'] = df_rows['dock'].astype(str)
        df_rows['timestamp'] = pd.to_datetime(df_rows['timestamp'])
        return df_rows

    def transform_to_train(self, df, value_column, future=True):
        # lat_dock_pos, long_dock_pos, geohash_dock = self.dock_positions()
        lat_dock_pos, long_dock_pos = self.dock_positions()

        df['long'] = df['dock'].map(long_dock_pos)
        df['lat'] = df['dock'].map(lat_dock_pos)
        # geohash = pd.get_dummies(df['dock'].map(geohash_dock))
        # combined_df = pd.concat([df, geohash], axis=1)
        df = df.sort_values(['dock', 'timestamp'])
        loop_list = [i for i in range(1, 10)] + ([-1, -2, -3] if future else [])
        loop_groupby = df.groupby('dock')
        for i in loop_list:
            df[f'{value_column}_{i}'] = loop_groupby[value_column].shift(i)
            # print(i)
        df = df.dropna(thresh=self.na_thresh)
        df = df.dropna(axis=0)
        df['hour'] = df.timestamp.dt.hour
        df['minute'] = df.timestamp.dt.minute
        df['day'] = df.timestamp.dt.weekday
        # df['empty_dock'] = 0
        # df.loc[(df['bikes_present_-1'] == 0) & (df['bikes_present_1'] != 0), 'empty_dock'] = 1
        # balanced_df = df[df['empty_dock'] == 0].sample(len(df[df['empty_dock'] == 1]))

        return df

      def transform(self, df, value_column='bikes_present', future=True):
        row_transformed = self.transform_to_rows(df, value_column)
        train_transform = self.transform_to_train(row_transformed, value_column, future)
        return train_transform

    def train_test_split(self, df, frac=0.2):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        timestamp_unique = df.timestamp.unique()
        bottom_date = timestamp_unique[round((len(timestamp_unique) - len(timestamp_unique) * frac))]
        # df = self.transform(df)
        train = df[df['timestamp'] < pd.to_datetime(bottom_date)]
        test = df[df['timestamp'] >= pd.to_datetime(bottom_date)]
        return train, test

    def create_empty_docks(self):
        bikes_df = self.combine_csvs(csv_name='bikes_present').reset_index(drop=True)
        total_df = self.combine_csvs(csv_name='total_docks').reset_index(drop=True)
        bikes_df = bikes_df[bikes_df['timestamp'].isin(total_df.timestamp.unique())]
        total_df = total_df[total_df['timestamp'].isin(bikes_df.timestamp.unique())]

        empty_df = pd.DataFrame(total_df.drop('timestamp', axis=1).values - bikes_df.drop('timestamp', axis=1).values,
                                columns=list(bikes_df.drop('timestamp', axis=1)))
        empty_df['timestamp'] = bikes_df.timestamp
        empty_df = empty_df.sort_values('timestamp')
        return empty_df


class BikesClassificationPipeline(BikesModelPipeline):
    def create_empty_column(self, df, number, value_column):
        df[f'{value_column}_empty_-{number}'] = 0
        df.loc[(df[f'{value_column}_-{number}'] == 0), f'{value_column}_empty_-{number}'] = 1
        return df

    def empty_dock_flag(self, df, value_column):
        df[f'{value_column}_empty'] = 0
        df.loc[(df[f'{value_column}'] == 0), f'{value_column}_empty'] = 1
        for i in range(1, 4):
            df = self.create_empty_column(df, i, value_column)
        return df

    def balance_classes(self, df, balance_column):
        empty_bikes = df[(df[balance_column] == 1) & (df[balance_column] != 0)]
        print(df[(df[balance_column] == 0)].shape)
        print(empty_bikes.shape)

        random_bikes = df[(df[balance_column] == 0)].sample(len(empty_bikes))
        train_full = pd.concat([empty_bikes, random_bikes])
        return train_full

    def transform(self, df, value_column='bikes_present', future=True):
        row_transformed = self.transform_to_rows(df, value_column)
        train_transform = self.transform_to_train(row_transformed, value_column, future)
        if future:
            empty_dock = self.empty_dock_flag(train_transform, value_column)
        else:
            empty_dock = train_transform
        return empty_dock

    def train_test_pipeline(self, df, value_column='bikes_present'):
        df = self.transform(df, value_column)
        balanced_df = self.balance_classes(df, value_column)
        train, test = self.train_test_split(balanced_df)
        return train, test


def fit_pred(train, test, target_col):
    print(train.shape)
    print(test.shape)
    # print(train.geohash.unique().shape)
    clf = ()
    clf.fit(
        train.drop(
            ['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2', 'bikes_present_-3'] + [
                target_col],
            axis=1),
        train[target_col])
    print(clf.predict_proba(
        test.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2', 'bikes_present_-3'] + [
            target_col],
                  axis=1)))
    test['pred'] = clf.predict(
        test.drop(['bikes_present_-1', 'dock', 'timestamp', 'bikes_present', 'bikes_present_-2', 'bikes_present_-3'] + [
            target_col],
                  axis=1))

    test['stay_empty'] = 0
    test['small_rule'] = 0
    test.loc[test['bikes_present_1'] == 0, 'stay_empty'] = 1
    test.loc[(test['bikes_present_1'] == 0) | (test['bikes_present_1'] == 1), 'small_rule'] = 1
    print(accuracy_score(test['empty'], test['pred']))
    print(accuracy_score(test['empty'], test['stay_empty']))
    print(accuracy_score(test['empty'], test['small_rule']))

    test.to_csv('test_pred.csv')
    return test


def empty_fit_pred(train, test, target_col):
    print(train.shape)
    print(test.shape)

    train_cols = ['lat', 'long', 'hour', 'minute', 'day'] + [f'empty_docks_{i}' for i in range(1, 10)]
    # train = train.sample(frac=0.1)
    clf = LogisticRegression()
    clf.fit(train[train_cols], train[target_col])
    # print(clf.predict_proba(test.drop(train_cols,axis=1)))
    test['pred'] = clf.predict(test[train_cols])

    test['stay_empty'] = 0
    test['small_rule'] = 0
    test.loc[test['empty_docks' + '_{}'.format(1)] == 0, 'stay_empty'] = 1
    test.loc[(test['empty_docks' + '_{}'.format(1)] == 0) | (
        test['empty_docks' + '_{}'.format(1)] == 1), 'small_rule'] = 1
    print(len(test))
    print(accuracy_score(test[target_col], test['pred']))
    print(accuracy_score(test[target_col], test['stay_empty']))
    print(accuracy_score(test[target_col], test['small_rule']))

    test.to_csv('test_pred.csv')
    return test


if __name__ == '__main__':
    from sklearn.metrics import mean_absolute_error, accuracy_score

    model_pipeline = BikesClassificationPipeline()
    bikes_df = model_pipeline.combine_csvs(csv_name='bikes_present')
    total_df = model_pipeline.combine_csvs(csv_name='total_docks')

    # bikes_df = model_pipeline.combine_csvs()
    bikes_df.timestamp = pd.to_datetime(bikes_df.timestamp)

    bikes_row = model_pipeline.transform_to_rows(bikes_df, 'bikes_present')
    print(len(bikes_row[bikes_row['bikes_present'] == 0]))
    print(len(bikes_row))
    total_row = model_pipeline.transform_to_rows(total_df, 'total_docks')

    full_row = bikes_row.merge(total_row, on=['timestamp', 'dock'])
    full_row['empty_docks'] = full_row['total_docks'] - full_row['bikes_present']
    # train_transform = model_pipeline.transform_to_train(bikes_row, 'bikes_present')
    # empty_dock = model_pipeline.empty_dock_flag(train_transform, 'bikes_present')
    # balanced_df = model_pipeline.balance_classes(empty_dock, 'bikes_present_empty_1')
    train_transform = model_pipeline.transform_to_train(full_row, 'empty_docks')
    # # print(len(train_transform[(train_transform['empty_docks'] == 0) & (train_transform['empty_docks_1'] == 0)]))
    # # print(len(train_transform[(train_transform['empty_docks'] != 0) & (train_transform['empty_docks_1'] != 0)]))
    # # print(len(train_transform[(train_transform['empty_docks'] == 0) & (train_transform['empty_docks_1'] != 0)]))
    # # print(len(train_transform[(train_transform['empty_docks'] != 0) & (train_transform['empty_docks_1'] == 0)]))
    # # print(len(train_transform))
    empty_dock = model_pipeline.empty_dock_flag(train_transform, 'empty_docks')

    balanced_df = model_pipeline.balance_classes(empty_dock, 'empty_docks_empty_-3')

    # bikes_transformed = model_pipeline.transform(bikes_df, 'bikes_present')
    # total_transformed = model_pipeline.transform(bikes_df, 'total_docks')

    train, test = model_pipeline.train_test_split(balanced_df)
    print(list(train))

    empty_fit_pred(train, test, 'empty_docks_empty_-3')
