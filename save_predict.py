import pandas as pd
import pickle
from model import BikesClassificationPipeline
from sklearn.linear_model import LogisticRegression


class TFLSave(BikesClassificationPipeline):
    def __init__(self):
        super().__init__()
        self.model_name = '{}_clf_{}.pkl'
        self.num_previous = 10
        self.data_file_path = 'test8{}.csv'

    def train_save(self, prediction_column):
        # new_data = self.combine_csvs(csv_name=prediction_column)
        # new_data = new_data.sort_values('timestamp')
        # transformed_df = self.transform(new_data, prediction_column)
        # # print(len(transformed_df))
        #
        # transformed_df.sample(frac=0.1).to_csv(f'{prediction_column}_transformed_data.csv')
        transformed_df = pd.read_csv(f'{prediction_column}_transformed_data.csv', index_col=0)
        # assert 1 == 0

        train_cols = ['dock', 'timestamp', prediction_column, prediction_column + '_empty'] + [
            prediction_column + '_{}_{}'.format('empty', str(-i)) for
            i in
            range(1, 4)] + [
                         prediction_column + '_{}'.format(str(-i)) for
                         i in
                         range(1, 4)]

        time_map = {15: '', 30: '_-1', 45: '_-2', 60: '_-3'}

        for i in [15, 30, 45, 60]:
            pred_column = prediction_column + '_empty' + time_map[i]
            balanced_df = self.balance_classes(transformed_df, pred_column)
            train, test = self.train_test_split(balanced_df)
            clf = LogisticRegression()
            clf.fit(train.drop(train_cols, axis=1), train[pred_column])
            with open(self.model_name.format(prediction_column, i), 'wb') as file:
                pickle.dump(clf, file)

    def full_predictions(self):
        self.create_empty_docks().to_csv(self.data_file_path.format('empty_docks'))
        # self.train_save('bikes_present'), self.train_save('empty_docks')
        self.train_save('empty_docks'), self.train_save('bikes_present')


class TFLPredict(BikesClassificationPipeline):
    def __init__(self):
        super().__init__()
        self.model_name = '{}_clf_{}.pkl'
        self.num_previous = 10
        self.data_file_path = 'test8{}.csv'

    def predict(self, prediction_column):
        new_data = pd.read_csv(self.data_file_path.format(prediction_column))
        new_data = new_data.tail(self.num_previous)
        row_data = self.transform(new_data, prediction_column, future=False)
        test_data = row_data.drop([prediction_column, 'timestamp', 'dock'], axis=1)
        prediction_df = row_data.copy()
        column_names = []

        for i in [15, 30, 45, 60]:
            with open(self.model_name.format(prediction_column, i), 'rb') as file:
                clf = pickle.load(file)
                current_column_name = '{}_{}_predictions'.format(prediction_column, i)
                prediction_df[current_column_name] = clf.predict(test_data)
                column_names.append(current_column_name)

        return prediction_df[['dock'] + column_names]

    def full_predictions(self):
        self.create_empty_docks().to_csv(self.data_file_path.format('empty_docks'))
        full_df = pd.concat([self.predict('bikes_present'), self.predict('empty_docks')], axis=1)
        return full_df


if __name__ == '__main__':
    obj = TFLPredict()
    obj.full_predictions().to_csv('sample_preds.csv', index=False)
