#%%
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from urllib.request import urlopen
import json
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import re

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ----------- MAP -----------

with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
    counties = json.load(response) # load map in json format

sheets_dict = pd.read_excel('data/metrics.xlsx', sheet_name=None)
data_dict = {}
metrics_dropdown = []
i = 0
for name, sheet in sheets_dict.items():
    sheet['sheet'] = name
    data_dict[name] = sheet
    metrics_dropdown.append({'label':name, 'value':i})
    i+=1

dep_dropdown = []
dep_list = data_dict[list(data_dict.keys())[0]]['dep']
for i, dep in enumerate(dep_list):
    dep_dropdown.append({'label':dep, 'value': i})

fig_map = px.choropleth(data_dict['taux_hosp'], geojson=counties, color="2020-03-18",
                    locations="dep", featureidkey="properties.code",
                    projection="mercator", labels={'02/01/2020':'saturation'},
                    color_continuous_scale=[(0, "rgb(223, 30, 38)"), (0.8, "rgb(243, 114, 32)"),
                                            (0.9, "rgb(251, 163, 26)"), (1, "rgb(255, 213, 0)")]
                   )
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=850)

# ---------------------------------

def metricName(value):
    for metric in metrics_dropdown:
        if(value == metric['value']):
            return metric['label']
    return None

# ----------- TRENDLINE -----------

fig_trend = px.line(data_dict['taux_hosp'], x=data_dict['taux_hosp'].columns,
                    y=data_dict['taux_hosp'][data_dict['taux_hosp']['dep']=='02'].values.flat,
                    title='Trend line')

# ----------- BAR CHART -----------

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=data_dict['taux_hosp']['2020-03-25'].values,
                y=data_dict['taux_hosp']['dep'].values,
                name="2020-03-18",
                marker_color='rgb(55, 83, 109)',
                orientation='h'
                ))
fig_bar.add_trace(go.Bar(x=data_dict['taux_hosp']['2020-03-25'].values,
                y=data_dict['taux_hosp']['dep'].values,
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

#%%

# ----------- DASHBOARD ARCHITECTURE -----------

app.layout = html.Div(
        [
            ######## TITLE ##############"
            html.Div(
                [
                html.Div(id='fordebug'),
                html.H1(
                    children='Covid-19 hospital tracker',
                    style={
                        'textAlign': 'center'
                    }
                )
            ]
        ),
            #************** BUTTONS ****************
            html.Div(
                ########## DATE ##########
                [
                    html.Div(
                [

                    #html.Button('-', id='buttonMinus'),

                    dcc.DatePickerSingle(
                    id='date-picker-single',
                    date=dt(2020, 3, 25)
                        )

                    #,
                    #html.Button('+', id='buttonPlus'),

                ], className="three columns"),

                ########## DROPDOWN METRIC 1 ##########
                    html.Div(
                [
                    dcc.Dropdown(
                        id='metric_1',
                        options=metrics_dropdown,
                        style={
                            'width': '250px',
                            },
                        value='0'
                        )], className="three columns"),

                ########## DROPDOWN METRIC 2 ##########
                    html.Div(
                [
                    dcc.Dropdown(
                        id='metric_2',
                        options=metrics_dropdown,
                        style={
                            'width': '250px',
                            },
                        value='0'
                        )
                ], className="three columns"),

                ########## DROPDOWN DEPARTMENT ##########
                    html.Div(
                [
                    dcc.Dropdown(
                        id='departments',
                        options=dep_dropdown,
                        style={
                            'width': '250px',
                            },
                        value=50
                        )
                    ], className="three columns")

                ]),

                #************** GRAPHS ****************

                html.Div(
                [

                    ########## MAP ##########

                    html.Div([

                        dcc.Graph(id="map", figure=fig_map),

                        ], className="seven columns"),

                    ########## TRENLINE ##########

                    html.Div([

                        html.Div([
                            dcc.Graph(figure=fig_trend)
                            ], className="row"),

                    ########## BAR CHART ##########

                        html.Div([
                            dcc.Graph(figure=fig_bar)
                            ], className="row")

                        ], className="five columns")
            ], className="eleven columns")
    ])

# ----------- CALLBACKS -------------------------

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('date-picker-single', 'date'),
     dash.dependencies.Input('metric_1', 'value')])
def update_figure(selected_date, selected_metric):

    date = dt.strptime(re.split('T| ', selected_date)[0], '%Y-%m-%d')
    date_string = date.strftime('%Y-%m-%d')
    metric_name = metricName(int(selected_metric))

    fig = px.choropleth(data_dict[metric_name], geojson=counties, color=date_string,
                    locations="dep", featureidkey="properties.code",
                    projection="mercator", labels={'02/01/2020':'saturation'},
                    color_continuous_scale=[(0, "rgb(223, 30, 38)"), (0.02, "rgb(243, 114, 32)"),
                                            (0.9, "rgb(251, 163, 26)"), (1, "rgb(255, 213, 0)")]
                   )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=850)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)