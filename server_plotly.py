import pandas as pd
import plotly.graph_objs as go

mapbox_access_token = "pk.eyJ1IjoiZHlzb250IiwiYSI6ImNqdXgybXF5NzBoNzkzenFybmJudnlkZ20ifQ.wd1TCNEDalY7PXlag-kC0w"


class ServerPlotTransform:
    def predictions_transform(self, bikes_present, bikes_total, predictions, metadata='metadata.json'):
        metadata = pd.read_json(metadata)
        metadata = metadata.T
        # site_lat = metadata.Lat
        # site_lon = metadata.Long
        # locations_name = metadata.Name

        present_latest = bikes_present.iloc[-1]
        total_latest = bikes_total.iloc[-1]

        metadata['present'] = [present_latest[i] for i in list(metadata.ID)]
        metadata['total'] = [total_latest[i] for i in list(metadata.ID)]

        predictions['dock'] = predictions['dock'].astype(int)
        metadata['ID'] = metadata['ID'].astype(int)
        with_predictions = metadata.merge(predictions, left_on='ID', right_on='dock').dropna()
        for i in range(1, 5):
            with_predictions[f'{i * 15}_colour'] = 'rgb(81, 81, 81)'
            with_predictions.loc[
                with_predictions[f'empty_docks_{i * 15}_predictions'] == 1, f'{i * 15}_colour'] = 'rgb(255, 0, 0)'
            with_predictions.loc[
                with_predictions[f'bikes_present_{i * 15}_predictions'] == 1, f'{i * 15}_colour'] = 'rgb(66, 134, 244)'

        return with_predictions

    def non_predictions_transform(self, bikes_present, bikes_total, metadata='metadata.json'):
        metadata = pd.read_json(metadata)
        metadata = metadata.T
        # site_lat = metadata.Lat
        # site_lon = metadata.Long
        # locations_name = metadata.Name

        present_latest = bikes_present.iloc[-1]
        total_latest = bikes_total.iloc[-1]

        metadata['present'] = [present_latest[i] for i in list(metadata.ID)]
        metadata['total'] = [total_latest[i] for i in list(metadata.ID)]
        for i in range(1, 5):
            metadata[f'{i * 15}_colour'] = 'rgb(81, 81, 81)'

        return metadata.dropna()


def slider_function(x, df):
    data = [

        go.Scattermapbox(
            lat=df['Lat'],
            lon=df['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=df['total'],
                color=df[f'{x}_colour'],
                opacity=0.7
            ),
        )
    ]

    layout = go.Layout(
        title='Bike Stations',
        autosize=True,
        hovermode='closest',
        showlegend=False,
        # width=1000,
        # height=700,
        margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0),
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=51.5,
                lon=-0.102
            ),
           # pitch=0,
            zoom=13,

            style='outdoors'
        ),
    )
    return {'data': data, 'layout': layout}
