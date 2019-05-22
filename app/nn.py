from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import numpy as np


class BikesNN:
    def __init__(self, time_step, ahead_pred, test_date):
        self.time_step = time_step
        self.ahead_pred = ahead_pred
        self.test_date = test_date
        self.train_x_list = []
        self.train_y_list = []
        self.test_x_list = []
        self.test_y_list = []
        self.test_meta = []

    def build_model(self, train_shape, test_shape):
        model = Sequential()
        model.add(LSTM(128, input_shape=(train_shape[1], train_shape[2]), activation='relu'))
        # model.add(LSTM(128, input_shape=(train_shape[1], train_shape[2]), activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def time_step_create_simple(self, x):
        array = x.drop(['dock', 'bikes_present_-1', 'timestamp', 'bikes_present', 'bikes_present_-2'], axis=1).values

        target = x['bikes_present_-1'].values
        date = x.timestamp.values
        meta = x[['dock', 'timestamp', 'bikes_present_-1']].values
        for i in range(self.time_step, len(x) - (1 + self.ahead_pred)):
            previous = array[(i - self.time_step):i]
            target_block = target[i + self.ahead_pred]

            if date[i] < self.test_date:
                self.train_x_list.append(previous.copy())
                self.train_y_list.append(target_block.copy())
            else:
                self.test_x_list.append(previous.copy())
                self.test_y_list.append(target_block.copy())
                self.test_meta.append(np.concatenate([meta[i + self.ahead_pred].copy(), meta[i]], axis=0))

    def create_train_test(self, df):
        df.groupby('dock').apply(self.time_step_create_simple)
        train_x_array = np.dstack(self.train_x_list)
        train_x_array = np.rollaxis(train_x_array, -1)
        train_y_array = np.stack(self.train_y_list)

        test_x_array = np.dstack(self.test_x_list)
        test_x_array = np.rollaxis(test_x_array, -1)
        test_y_array = np.stack(self.test_y_list)

        model = self.build_model(train_x_array.shape, train_y_array.shape)
        model.fit(train_x_array, train_y_array, batch_size=128, epochs=50)
        test_df = pd.DataFrame(np.array(self.test_meta))
        test_df = pd.concat([test_df, pd.DataFrame(model.predict(test_x_array))], axis=1)

        # test_df['pred'] = self.model.predict(test_x_array)
        # test_df['pred']
        test_df.to_csv('nn_route_pred.csv')
        print(df)


if __name__ == '__main__':
    from model import BikesModelPipeline
    import pandas as pd

    model_pipeline = BikesModelPipeline()
    bikes_df = model_pipeline.combine_csvs()
    bikes_df.timestamp = pd.to_datetime(bikes_df.timestamp)

    rows_df = model_pipeline.transform_to_rows(bikes_df)
    # rows_df = rows_df.iloc[0:10000, :]
    bikes_df = model_pipeline.transform_to_train(rows_df)
    timestamp_unique = bikes_df.timestamp.unique()

    bottom_date = timestamp_unique[round((len(timestamp_unique) - len(timestamp_unique) * 0.1))]
    BikesNN(time_step=10, ahead_pred=1, test_date=bottom_date).create_train_test(bikes_df)
