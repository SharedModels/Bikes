from keras.models import Sequential
from keras.layers import LSTM, Dense
from data_pull import pull_remove_na
import numpy as np
import random


def convert_to_train(data, num_back, num_ahead, shuffle=False):
    x_list = []
    y_list = []
    data_values = data.drop('timestamp', axis=1).values

    for i in range(0, len(data) - far_back):
        x_list.append(data_values[i:i + num_back, :].copy())
        y_list.append(data_values[i + num_back + (num_ahead - 1):i + num_back + num_ahead, :].copy())
    if shuffle:
        shuffled_id = [i for i in range(len(data) - num_back)]
        random.shuffle(shuffled_id)
        x_list = [x_list[i] for i in shuffled_id]
        y_list = [y_list[i] for i in shuffled_id]

    x = np.stack(x_list, axis=0)
    y = np.vstack(y_list)
    return x, y


def mae_2d(a, b):
    return np.abs(a - b).sum() / len(a)


data = pull_remove_na()

train = data.head(round(len(data) / 0.8))
test = data.tail(round(len(data) / 0.2))

far_back = 10
far_ahead = 1

x, y = convert_to_train(train, far_back, far_ahead, shuffle=True)
test_x, test_y = convert_to_train(test, 10, 1)

# compare_y = test_y[1:, :]
# prev_y = test_y[:-1, :]
# print(mae_2d(compare_y, prev_y))

model = Sequential()
model.add((LSTM(100, activation='relu', input_shape=(far_back, x.shape[2]))))
model.add((Dense(50, activation='relu')))
model.add(Dense(y.shape[1]))
model.compile(loss='mse', optimizer='adam')
# fit network
model.fit(x, y, epochs=1, batch_size=128)

print(mae_2d(test_y, model.predict(test_x)))

# print(x.shape)
# print(y.shape)
