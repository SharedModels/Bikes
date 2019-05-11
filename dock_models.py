import pandas as pd
from model import BikesModelPipeline
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

full_csv = BikesModelPipeline().combine_csvs()
full_csv = full_csv.dropna(axis=1, thresh=5)
# print(full_csv)
full_csv = full_csv.fillna(method='bfill')
model_dict = {}


def train_apply(x):
    if x.name == 'timestamp':
        return
    original_array = x.values
    train_x_list = []
    train_y_list = []
    test_x_list = []
    test_y_list = []
    test_previous = []
    test_start = round(len(original_array) * 0.75)
    for i in range(7, len(original_array) - 1):
        if i < test_start:
            array_list = [original_array[j] for j in range(i - 7, i - 1)]
            train_x_list.append(np.array(array_list))
            train_y_list.append(original_array[i])
        else:
            array_list = [original_array[j] for j in range(i - 7, i - 1)]
            test_x_list.append(np.array(array_list))
            test_y_list.append(original_array[i])
            test_previous.append(original_array[i - 1])

    train_x_array = np.array(train_x_list)
    test_x_array = np.array(test_x_list)
    train_y_array = np.array(train_y_list)
    test_y_array = np.array(test_y_list)
    test_previous_array = np.array(test_previous)
    clf = RandomForestRegressor()
    clf.fit(train_x_array, train_y_array)

    if mean_absolute_error(test_y_array, clf.predict(test_x_array)) < mean_absolute_error(test_y_array, test_previous_array):
        print(x.name, mean_absolute_error(test_y_array, clf.predict(test_x_array)),
              mean_absolute_error(test_y_array, test_previous_array))
    # clf.predict(test_x_array)
    # print(x.name, clf.score(train_array, test_array))
    model_dict[x.name] = {'data': x, 'model': clf}


full_csv.apply(train_apply, axis=0)
