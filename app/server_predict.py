import pandas as pd
import pickle
from server_model_transform import BikesModelTransform


class ServerPredict:
    def __init__(self, model_name='{}_clf_{}.pkl'):
        self.transform_obj = BikesModelTransform()
        self.model_name = model_name

    def predict(self, df, prediction_column):
        # test_data = df.drop([prediction_column, 'timestamp', 'lat', 'long'], axis=1)
        test_data = df.drop([prediction_column, 'timestamp', 'dock'], axis=1)
        test_data = pd.get_dummies(test_data)
        prediction_df = df.copy()
        column_names = []

        for i in [15, 30, 45, 60]:
            with open(self.model_name.format(prediction_column, i), 'rb') as file:
                clf = pickle.load(file)
                # print(clf.coef_)
                current_column_name = '{}_{}_predictions'.format(prediction_column, i)
                prediction_df[current_column_name] = clf.predict(test_data)
                column_names.append(current_column_name)

        return prediction_df[['dock'] + column_names]

    def full_predictions(self, bikes_df, empty_df):
        full_df = self.predict(bikes_df, 'bikes_present').merge(self.predict(empty_df, 'empty_docks'), on='dock')
        # full_df = pd.concat([self.predict(bikes_df, 'bikes_present'), self.predict(empty_df, 'empty_docks')], axis=1)
        return full_df
