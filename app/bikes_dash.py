import dash
import dash_core_components as dcc
import dash_html_components as html
import server_pipeline as server_pipeline

interval_time = 5 * 60

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
pipeline_obj = server_pipeline.ParallelServerPipeline(interval_time=interval_time)
pipeline_obj.update_and_save()
pipeline_obj.interval_update(-1)

app.layout = html.Div([
    dcc.Graph(
        id='current bikes',
        figure=pipeline_obj.slider_update(15)

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
        interval=interval_time * 1000,  # in milliseconds
        n_intervals=0)

], style={'height': '100%'})


# @app.callback(
#     dash.dependencies.Output('current bikes', 'figure'),
#     [dash.dependencies.Input('interval-component', 'n_intervals'),
#      dash.dependencies.Input('my-slider', 'value')])
# def interval_update(n_intervals, value):
#     # if prev_interval != n_intervals:
#     obj.interval_update(n_intervals)
#     # prev_interval = n_intervals
#     return obj.slider_update(value)
@app.callback(
    dash.dependencies.Output('current bikes', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals'),
     dash.dependencies.Input('my-slider', 'value')])
def interval_update(n_intervals, value):
    return pipeline_obj.combined_update(n_intervals, value)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=80)
    # app.run_server()
