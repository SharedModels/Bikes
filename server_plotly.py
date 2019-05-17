import pandas as pd
import plotly.graph_objs as go

mapbox_access_token = "pk.eyJ1IjoiZHlzb250IiwiYSI6ImNqdXgybXF5NzBoNzkzenFybmJudnlkZ20ifQ.wd1TCNEDalY7PXlag-kC0w"


class ServerPlotTransform:
    def __init__(self, metadata='metadata.json'):
        self.metadata = self.initiate_metadata(metadata)

    def initiate_metadata(self, metadata):
        metadata = pd.read_json(metadata)
        metadata = metadata.T
        metadata['ID'] = metadata['ID'].astype(int)
        return metadata

    def predictions_transform(self, bikes_present, bikes_total, predictions):
        # TODO There is loads here that could be more efficient but requires more thought
        metadata = self.metadata
        present_latest = bikes_present.iloc[-1]
        total_latest = bikes_total.iloc[-1]

        metadata['present'] = [present_latest[i] for i in list(metadata.ID)]
        metadata['total'] = [total_latest[i] for i in list(metadata.ID)]
        metadata = metadata.dropna()
        metadata['present_text'] = metadata['present'].astype(int).astype(str) + ' bikes currently at this station'
        metadata['total_text'] = metadata['total'].astype(int).astype(str) + ' docks currently for this station'

        predictions['dock'] = predictions['dock'].astype(int)
        with_predictions = metadata.merge(predictions, left_on='ID', right_on='dock').dropna()
        for i in range(1, 5):
            with_predictions[f'{i * 15}_colour'] = 'rgb(81, 81, 81)'
            with_predictions.loc[
                with_predictions[f'empty_docks_{i * 15}_predictions'] == 1, f'{i * 15}_colour'] = 'rgb(255, 0, 0)'
            with_predictions.loc[
                with_predictions[f'bikes_present_{i * 15}_predictions'] == 1, f'{i * 15}_colour'] = 'rgb(66, 134, 244)'

        return with_predictions

    def non_predictions_transform(self, bikes_present, bikes_total):
        metadata = self.metadata

        present_latest = bikes_present.iloc[-1]

        total_latest = bikes_total.iloc[-1]

        metadata['present'] = [present_latest[i] for i in list(metadata.ID)]
        metadata['total'] = [total_latest[i] for i in list(metadata.ID)]
        metadata = metadata.dropna()
        metadata['present_text'] = metadata['present'].astype(int).astype(str) + ' bikes currently at this station'
        metadata['total_text'] = metadata['total'].astype(int).astype(str) + ' docks currently for this station'

        for i in range(1, 5):
            metadata[f'{i * 15}_colour'] = 'rgb(81, 81, 81)'

        return metadata.dropna()

    def slider_function(self, x, df):
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
                text=df['Name'] + "<br />" + df['present_text'] + "<br />" + df['total_text'],
                hoverinfo='text'
            )
        ]
        return data

    def layout(self):

        layout = go.Layout(
            title='Bike Stations',
            autosize=True,
            hovermode='closest',
            showlegend=False,
            uirevision="none",
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
        return layout
