from server_scrape import ServerScrape
from server_model_transform import BikesModelTransform
from server_predict import ServerPredict
from server_plotly import ServerPlotTransform
import datetime
import pandas as pd
import time


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
        self.layout = self.plot_transformer.layout()

    def calculate_num_keep(self):
        return int((self.training_interval * self.model_previous) / self.interval_time)

    def create_loop_list(self):
        return [int(i * self.training_interval / self.interval_time) for i in range(self.model_previous)]

    def update(self):
        bikes_present, empty_docks, total_docks = self.scraper.update(self.num_keep)
        print(bikes_present.shape)
        if len(bikes_present) < self.num_keep - 1:
            self.plot_df = self.plot_transformer.non_predictions_transform(bikes_present, total_docks)
            return self.plot_df
            # return {'data': self.plot_transformer.slider_function(15, self.plot_df), 'layout': self.layout}

        transformed_bikes = self.model_transformer.transform(bikes_present, 'bikes_present', loop_list=self.loop_list,
                                                             future=False)
        transformed_empty = self.model_transformer.transform(empty_docks, 'empty_docks', loop_list=self.loop_list,
                                                             future=False)

        predictions = self.predictor.full_predictions(transformed_bikes, transformed_empty)
        plot_df = self.plot_transformer.predictions_transform(bikes_present, total_docks, predictions)
        self.plot_df = plot_df
        return self.plot_df

    def interval_update(self, interval):
        if interval == self.prev_interval:
            return None

        self.prev_interval = interval
        return {'data': self.plot_transformer.slider_function(15, self.update()), 'layout': self.layout}

    def slider_update(self, x):
        return {'data': self.plot_transformer.slider_function(x, self.plot_df), 'layout': self.layout}


class ParallelServerPipeline(ServerPipeline):
    def __init__(self, save_path='plot_df.csv', interval_time=60, model_previous=10, training_interval=15 * 60):
        super().__init__(interval_time=interval_time, model_previous=model_previous,
                         training_interval=training_interval)
        self.save_path = save_path

    def combined_update(self, interval, x):
        # print(interval)
        # if interval == self.prev_interval:
        #     return None

        self.plot_df = pd.read_csv(self.save_path)
        # self.prev_interval = interval
        return self.slider_update(x)

    def interval_update(self, interval):
        # print(interval, self.prev_interval)
        if interval == self.prev_interval:
            return None

        self.plot_df = pd.read_csv(self.save_path)
        self.prev_interval = interval
        return {'data': self.plot_transformer.slider_function(15, self.update()), 'layout': self.layout}

    def update_and_save(self):
        df = self.update()
        df.to_csv(self.save_path)

    def parallel_loop(self):
        while True:
            update_start = datetime.datetime.now()
            self.update_and_save()
            update_finish = datetime.datetime.now()
            time.sleep(self.interval_time - (update_finish - update_start).seconds)


if __name__ == '__main__':
    import bikes_dash

    obj = ParallelServerPipeline(interval_time=bikes_dash.interval_time)
    obj.parallel_loop()
