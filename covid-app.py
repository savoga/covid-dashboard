import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from urllib.request import urlopen
import json
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ----------- MAP -----------

with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
    counties = json.load(response) # load map in json format

df = pd.read_csv("data.csv",
                   dtype={"code": str})

fig_map = px.choropleth(df, geojson=counties, color="saturation",
                    locations="code", featureidkey="properties.code",
                    projection="mercator"
                   )
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=900)

# ----------- TRENDLINE -----------

df_trend = pd.read_csv("graph_values.csv")
fig_trend = px.line(df_trend, x="day", y="value", title='Trend line')

# ----------- BAR CHART -----------

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=df['code'],
                y=df['saturation'],
                name='Saturation',
                marker_color='rgb(55, 83, 109)',
                orientation='h'
                ))
fig_bar.add_trace(go.Bar(x=df['code'],
                y=df['saturation'],
                name='Availability',
                marker_color='rgb(26, 118, 255)',
                orientation='h'
                ))


fig_bar.update_layout(
    title='Saturation / Availability',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Saturation',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)

# ----------- DASHBOARD ARCHITECTURE -----------

app.layout = html.Div(
        [
            html.Div(
                [
                html.H1(
                    children='Covid-19 hospital tracker',
                    style={
                        'textAlign': 'center'
                    }
                )
            ]
        ),
            html.Div(
                [

                html.Button('-', id='buttonMinus'),

                dcc.DatePickerSingle(
                id='date-picker-single',
                date=dt(2019, 1, 1)
                    ),

                html.Button('+', id='buttonPlus'),

                dcc.Dropdown(
                    id='metric',
                    options=[
                        {'label': 'Saturation', 'value': '0'},
                        {'label': 'Number of private hospitals', 'value': '1'},
                        ],
                    style={
                        'width': '250px',
                        },
                    value='0'
                    ),

                dcc.Dropdown(
                    id='metric-3D',
                    options=[
                        {'label': 'Saturation', 'value': '0'},
                        {'label': 'Number of private hospitals', 'value': '1'},
                        ],
                    style={
                        'width': '250px',
                        },
                    value='1'
                    ),

                dcc.Dropdown(
                    id='departments',
                    options=[
                        {'label': 'Manche', 'value': '50'},
                        {'label': 'Morbihan', 'value': '56'}
                        ],
                    style={
                        'width': '250px',
                        },
                    value=50
                    )

                ], style={'columnCount': 4}
            ),
            html.Div(
                [
                    html.Div([
                        dcc.Graph(figure=fig_map),
                        ], className="six columns"),
                    html.Div([
                        html.Div([
                            dcc.Graph(figure=fig_trend)
                            ], className="row"),
                        html.Div([
                            dcc.Graph(figure=fig_bar)
                            ], className="row")
                        ], className="six columns")
            ], className="row")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)