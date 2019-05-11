import plotly.offline as py
import plotly.graph_objs as go

import pandas as pd

mapbox_access_token = "pk.eyJ1IjoiZHlzb250IiwiYSI6ImNqdXgybXF5NzBoNzkzenFybmJudnlkZ20ifQ.wd1TCNEDalY7PXlag-kC0w"

metadata = pd.read_json("metadata.json")
metadata = metadata.T
site_lat = metadata.Lat
site_lon = metadata.Long
locations_name = metadata.Name

preds = pd.read_csv("sample_preds.csv")
present = pd.read_csv("present_server_test.csv")
total = pd.read_csv("docks_server_test.csv")

present_latest = present.iloc[-1]
total_latest = total.iloc[-1]

metadata['present'] = [present_latest[i] for i in list(metadata.ID)]
metadata['total'] = [total_latest[i] for i in list(metadata.ID)]

preds['dock'] = preds['dock'].astype(int)
metadata['ID'] = metadata['ID'].astype(int)
with_predictions = metadata.merge(preds, left_on='ID', right_on='dock').dropna()

# def status_test(empty, full):
#     if empty:
#         return "In 15 minutes this dock will likely be empty"
#     elif full:
#         return "In 15 minutes this dock will likely be full"
#     else:
#         return "In 15 minutes this dock will likely be neither full nor empty"


# l = []
# for i in range(len(metadata)):
#     l.append(status_test(metadata['15_mins_empty'].values[i], metadata['15_mins_full'].values[i]))

# metadata['15_status'] = l
# metadata = metadata.dropna()

print(list(with_predictions))


def slider_function(x):
    pred_full = with_predictions[with_predictions[f'empty_docks_{x}_predictions'] == 1]
    pred_empty = with_predictions[with_predictions[f'bikes_present_{x}_predictions'] == 1]
    remaining = with_predictions[(with_predictions[f'bikes_present_{x}_predictions'] == 0) & (
        with_predictions[f'empty_docks_{x}_predictions'] == 0)]

    data = [

        go.Scattermapbox(
            lat=pred_full['Lat'],
            lon=pred_full['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=pred_full['total'],
                color='rgb(255, 0, 0)',
                opacity=0.7
            ),
            # text=pred_full['Name'] + "<br />" + pred_full['15_status'],
            # hoverinfo='text'
        ),
        go.Scattermapbox(
            lat=pred_full['Lat'],
            lon=pred_full['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=pred_full['present'],
                color='rgb(242, 177, 172)',
                opacity=0.7
            ),
            # text=pred_full['Name'] + "<br />" + pred_full['15_status'],
            # hoverinfo='text'
        ),

        go.Scattermapbox(
            lat=pred_empty['Lat'],
            lon=pred_empty['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=pred_empty['total'],
                color='rgb(0, 97, 255)',
                opacity=0.7
            ),
            # text=pred_empty['Name'] + "<br />" + pred_empty['15_status'],
            # hoverinfo='text'
        ),
        go.Scattermapbox(
            lat=pred_empty['Lat'],
            lon=pred_empty['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=pred_empty['present'],
                color='rgb(66, 134, 244)',
                opacity=0.7
            ),
            # text=pred_empty['Name'] + "<br />" + pred_empty['15_status'],
            # hoverinfo='text'
        ),

        go.Scattermapbox(
            lat=remaining['Lat'],
            lon=remaining['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=remaining['total'],
                color='rgb(81, 81, 81)',
                opacity=0.7
            ),
            # text=remaining['Name'] + "<br />" + remaining['15_status'],
            # hoverinfo='text'
        ),
        go.Scattermapbox(
            lat=remaining['Lat'],
            lon=remaining['Long'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=remaining['present'],
                color='rgb(132, 132, 132)',
                opacity=0.7
            ),
            # text=remaining['Name'] + "<br />" + remaining['15_status'],
            # hoverinfo='text'
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
            t=0),
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=51.5,
                lon=-0.102
            ),
            pitch=0,
            zoom=13,

            style='outdoors'
        ),
    )
    return {'data': data, 'layout': layout}

# fig = go.Figure(data=slider_function(15)['data'], layout=slider_function(15)['layout'])
# py.plot(fig, filename='bike_locs.html')
