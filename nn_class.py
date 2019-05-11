from keras.models import Sequential
from keras.layers import Dense


class SimpleNN:
    def build_model(self, input_dim, output_dim):
        self.model = Sequential()
        self.model.add(Dense(64, input_shape=(input_dim,), activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        # self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1, activation='softmax'))

        self.model.compile(optimizer='adam', loss='hinge')
        return self.model

    def fit(self, train_x, train_y, epoch, batch_size):
        self.build_model(train_x.shape[1], train_y.shape[0])
        self.model.fit(train_x, train_y, epochs=epoch, batch_size=batch_size)

    def predict(self, test_x):
        return self.model.predict(test_x)
