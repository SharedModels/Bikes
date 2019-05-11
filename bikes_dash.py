import dash
import dash_core_components as dcc
import dash_html_components as html
import plotter

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(
        id='current bikes',
        figure=plotter.slider_function(15)

    ), html.Div([dcc.Slider(
        id='my-slider',
        min=15,
        max=60,
        step=15,
        value=15,
        marks={i: '{}'.format(i) for i in [15, 30, 45, 60]},
    )], style={'width': '20%', 'padding-left': '40%', 'padding-right': '40%', 'margin-bottom': 0}),

], style={'margin-bottom': 0})
# app.css.append_css({
#     'external_url': (
#         '._dash-undo-redo {display: none;}'
#     )
# })


@app.callback(
    dash.dependencies.Output('current bikes', 'figure'),
    [dash.dependencies.Input('my-slider', 'value')])
def update_output(value):
    return plotter.slider_function(value)


if __name__ == '__main__':
    app.run_server()
