from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from lightgbm import LGBMClassifier
import pandas as pd
import pickle
from server_model_transform import BikesModelTransform
from server_predict import ServerPredict


class ServerModelTrain:
    # def __init__(self):

    def create_binary_variable(self, y):
        binary_y = pd.Series([0 for i in range(len(y))], index=y.index)
        binary_y[y == 0] = 1
        binary_y = binary_y.rename(y.name)
        return binary_y

    def balance_classes(self, X, y):
        balance_number = len(y[y == 1])
        true_y_index = y == 1
        negative_y = y[y == 0].sample(balance_number)
        true_X = X[true_y_index]
        true_y = y[true_y_index]
        negative_X = X[X.index.isin(negative_y.index)]
        return pd.concat([true_X, negative_X]), pd.concat([true_y, negative_y])

    def fit_pipeline(self, df, target_col, model_extra=''):
        # NO BIKES PRESENT = 1, I.E EMPTY DOCK
        # NO EMPTY DOCKS = 1, I.E FULL DOCK
        # train = df.drop(['timestamp', 'lat', 'long', target_col] + [target_col + f'_-{i}' for i in range(1, 5)], axis=1)
        train = df.drop(['timestamp', 'lat', 'long', target_col] + [target_col + f'_-{i}' for i in range(1, 5)], axis=1)
        train = pd.get_dummies(train)
        map_dict = {i: i * 15 for i in range(1, 5)}

        for i in range(1, 5):
            clf = LogisticRegression()
            y = df[target_col + f'_-{i}']
            y = self.create_binary_variable(y)
            X, y = self.balance_classes(train, y)
            print(X.shape)
            clf.fit(X, y)
            with open(target_col + f'_clf_{map_dict[i]}{model_extra}.pkl', 'wb') as file:
                pickle.dump(clf, file)


def train_all():
    obj = ServerModelTrain()
    transformer = BikesModelTransform()

    bikes_present = pd.concat([pd.read_csv('test7bikes_present.csv'), pd.read_csv('test8bikes_present.csv')])
    total_docks = pd.concat([pd.read_csv('test7total_docks.csv'), pd.read_csv('test8total_docks.csv')])
    total_docks = total_docks[total_docks['timestamp'].isin(bikes_present.timestamp.values)]
    empty_docks = total_docks.drop('timestamp', axis=1) - bikes_present.drop('timestamp', axis=1).values
    empty_docks['timestamp'] = bikes_present['timestamp']
    transformed_bikes = transformer.transform(bikes_present, 'bikes_present')
    obj.fit_pipeline(transformed_bikes, 'bikes_present')
    transformed_empty = transformer.transform(empty_docks, 'empty_docks')
    obj.fit_pipeline(transformed_empty, 'empty_docks')


def find_accuracy():
    predictor = ServerPredict(model_name='{}_clf_{}_test.pkl')
    obj = ServerModelTrain()
    transformer = BikesModelTransform()

    bikes_present = pd.concat([pd.read_csv('test7bikes_present.csv'), pd.read_csv('test8bikes_present.csv'),
                               pd.read_csv('test9bikes_present.csv')])
    test_bikes = bikes_present.tail(round(len(bikes_present) / 3))
    train_bikes = bikes_present.head(round(len(bikes_present) / (3 / 2)))

    transformed_train = transformer.transform(train_bikes, 'bikes_present')
    transformed_test = transformer.transform(test_bikes, 'bikes_present')

    obj.fit_pipeline(transformed_train, 'bikes_present', model_extra='_test')

    test_predict_df = transformed_test.drop(
        ['bikes_present_-1', 'bikes_present_-2', 'bikes_present_-3', 'bikes_present_-4'], axis=1)
    binary_test = [obj.create_binary_variable(transformed_test[i]) for i in
                   ['bikes_present_-1', 'bikes_present_-2', 'bikes_present_-3', 'bikes_present_-4']]

    pred_df = predictor.predict(test_predict_df, 'bikes_present')
    with_preds = pd.concat(binary_test + [pred_df], axis=1)
    print(len(with_preds))
    print(len(with_preds[with_preds['bikes_present_-1'] == with_preds['bikes_present_15_predictions']]))
    print(
        len(with_preds[with_preds['bikes_present_-1'] == with_preds['bikes_present_15_predictions']]) / len(with_preds))


if __name__ == '__main__':
    # find_accuracy()
    train_all()
