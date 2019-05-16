import pandas as pd
from server_scrape import ServerScrape
from server_model_transform import BikesModelTransform
from server_predict import ServerPredict
from server_plotly import ServerPlotTransform, slider_function


class ServerPipeline:
    def __init__(self, interval_time=60, model_previous=10, training_interval=15 * 60):
        self.interval_time = interval_time
        self.model_previous = model_previous
        self.training_interval = training_interval
        self.scraper = ServerScrape()
        self.model_transformer = BikesModelTransform()
        self.predictor = ServerPredict()
        self.plot_transformer = ServerPlotTransform()
        self.num_keep = self.calculate_num_keep()
        self.loop_list = self.create_loop_list()
        self.plot_df = None
        self.prev_interval = -2

    def calculate_num_keep(self):
        return int((self.training_interval * self.model_previous) / self.interval_time)

    def create_loop_list(self):
        return [int(i * self.training_interval / self.interval_time) for i in range(self.model_previous)]

    def interval_update(self, interval):
        if interval == self.prev_interval:
            return None
        bikes_present, empty_docks, total_docks = self.scraper.update(self.num_keep)
        print(bikes_present.shape)
        if len(bikes_present) < self.num_keep - 1:
            self.plot_df = self.plot_transformer.non_predictions_transform(bikes_present, total_docks)
            return slider_function(15, self.plot_df)

        transformed_bikes = self.model_transformer.transform(bikes_present, 'bikes_present', loop_list=self.loop_list,
                                                             future=False)
        transformed_empty = self.model_transformer.transform(empty_docks, 'empty_docks', loop_list=self.loop_list,
                                                             future=False)

        predictions = self.predictor.full_predictions(transformed_bikes, transformed_empty)
        plot_df = self.plot_transformer.predictions_transform(bikes_present, total_docks, predictions)
        self.plot_df = plot_df
        self.prev_interval = interval
        return slider_function(15, self.plot_df)

    def slider_update(self, x):
        return slider_function(x, self.plot_df)


if __name__ == '__main__':
    import time

    obj = ServerPipeline(interval_time=5, training_interval=10)
    while True:
        time.sleep(1)
        a = obj.interval_update()
        print(a)
