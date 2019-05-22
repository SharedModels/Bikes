import pandas as pd
from model import BikesModelPipeline

model_pipeline = BikesModelPipeline()
# bikes_df = model_pipeline.combine_csvs()
bikes_df = pd.read_csv('test8empty_docks.csv', index_col=0)
bikes_df.timestamp = pd.to_datetime(bikes_df.timestamp)

rows_df = model_pipeline.transform_to_rows(bikes_df)
# rows_df = rows_df.iloc[0:10000, :]
bikes_df = model_pipeline.transform_to_train(rows_df)

empty_bikes = bikes_df[(bikes_df['bikes_present_-1'] == 0) & (bikes_df['bikes_present_1'] != 0)]
print(100 * len(empty_bikes) / len(bikes_df))
