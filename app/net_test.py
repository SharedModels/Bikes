from keras.models import Sequential
from keras.layers import LSTM, Dense
from data_pull import pull_remove_na
import numpy as np
import random

data = pull_remove_na()
far_back = 10
far_ahead = 1
x_list = []
y_list = []
data_values = data.drop('timestamp', axis=1).values

for i in range(0, len(data) - far_back):
    x_list.append(data_values[i:i + far_back, :].copy())
    y_list.append(data_values[i + far_back:i + far_back + far_ahead, :].copy())

shuffled_id = [i for i in range(len(data) - far_back)]
random.shuffle(shuffled_id)
shuffled_x = [x_list[i] for i in shuffled_id]
shuffled_y = [y_list[i] for i in shuffled_id]

x = np.stack(shuffled_x, axis=0)
y = np.vstack(shuffled_y)

model = Sequential()
model.add((LSTM(100, activation='relu', input_shape=(far_back, x.shape[2]))))
model.add((Dense(50, activation='relu')))
model.add(Dense(y.shape[1]))
model.compile(loss='mse', optimizer='adam')
# fit network
model.fit(x, y, epochs=10, batch_size=128)

# print(x.shape)
# print(y.shape)
