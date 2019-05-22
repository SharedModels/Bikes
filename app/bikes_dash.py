import dash
import dash_core_components as dcc
import dash_html_components as html
import server_pipeline

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
obj = server_pipeline.ServerPipeline(interval_time=30)
obj.interval_update(-1)

app.layout = html.Div([
    dcc.Graph(
        id='current bikes',
        figure=obj.slider_update(15)

    )
    , html.Div([dcc.Slider(
        id='my-slider',
        min=15,
        max=60,
        step=15,
        value=15,
        marks={i: '{}'.format(i) for i in [15, 30, 45, 60]},
    )], style={'width': '20%', 'padding-left': '40%', 'padding-right': '40%', 'margin-bottom': '0%'})
    ,
    dcc.Interval(
        id='interval-component',
        interval=30 * 1000,  # in milliseconds
        n_intervals=0)

], style={'height': '100%'})


@app.callback(
    dash.dependencies.Output('current bikes', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals'),
     dash.dependencies.Input('my-slider', 'value')])
def interval_update(n_intervals, value):
    # if prev_interval != n_intervals:
    obj.interval_update(n_intervals)
    # prev_interval = n_intervals
    return obj.slider_update(value)


if __name__ == '__main__':
    app.run_server()
