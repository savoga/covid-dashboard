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
server = app.server

with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
    counties = json.load(response) # load map in json format

# dictionnaire des départements: code-->nom du département
df = pd.read_csv('data/departements-france.csv')
dict_depart={}
code=list(df['code_departement'].values)
nom=list(df['nom_departement'].values)
for i in range(len(df)):
    dict_depart[code[i]]=nom[i]

sheets_dict = pd.read_excel('data/metrics.xlsx', sheet_name=None)
data_dict = {}
metrics_dropdown = []
i = 0
for name, sheet in sheets_dict.items():
    sheet['sheet'] = name
    data_dict[name] = sheet
    metrics_dropdown.append({'label':name, 'value':i})
    i+=1

# this drop down is for the labels , it contains names of the departments
dep_dropdown2 = []
dep_list = data_dict[list(data_dict.keys())[0]]['dep']
for i, dep in enumerate(dep_list):
    dep_dropdown2.append({'label':dep, 'value': i})

# this drop down is for the trendline , it contains department's code
dep_dropdown = []
dep_list = data_dict[list(data_dict.keys())[0]]['dep']
for i, dep in enumerate(dep_list):
    dep_dropdown.append({'label':dict_depart[dep], 'value': i})

first_DF = data_dict[next(iter(data_dict))]

# ----------- MAP -----------

fig_map = px.choropleth(first_DF, geojson=counties, color="2020-03-18",
                    locations="dep", featureidkey="properties.code",
                    projection="mercator"
                   )
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=850)

# ---------------------------------

def metricName(value):
    for metric in metrics_dropdown:
        if(value == metric['value']):
            return metric['label']
    return None


def departmentNumber(value):
    for dep in dep_dropdown2:
        if(value == dep['value']):
            return dep['label']
    return None



# ----------- TRENDLINE -----------

fig_trend = px.line(first_DF, x=first_DF.columns[1:],
                    y=first_DF[first_DF['dep']=='01'].values.flat[1:],
                    title='Trend line')

# ----------- BAR CHART -----------


def Top_indices(liste,N):
    return sorted(range(len(liste)), key=lambda i: liste[i], reverse=True)[:N]

def lowest_indices(liste,N):
    return sorted(range(len(liste)), key=lambda i: liste[i], reverse=False)[:N]

X0=list(first_DF['2020-03-25'].values)
Y0=list(first_DF['dep'].values)

indices1=Top_indices(X0,10)

X=[int(X0[i]) for i in indices1]
Y=[dict_depart[Y0[i]] for i in indices1]

fig_bar1 = go.Figure()
fig_bar1.add_trace(go.Bar(x=X,y=Y,
                name="2020-03-18",
                marker_color='rgb(55, 83, 109)',
                orientation='h'
                ))


fig_bar1.update_layout(
    #title='Saturation / Availability',
    #xaxis_tickfont_size=14,
    title='Saturation',
    barmode='stack',
    xaxis={'categoryorder':'total descending'},
    yaxis=dict(
        autorange="reversed",
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        #bgcolor='rgba(255, 255, 255, 0)',
        #bordercolor='rgba(255, 255, 255, 0)'
    ),
    #barmode='group',
    bargap=0.05, # gap between bars of adjacent location coordinates.
    bargroupgap=0.05 # gap between bars of the same location coordinate.
)

# char bar 2 :

indices2=lowest_indices(X0,10)
X=[int(X0[i]) for i in indices2]
Y=[dict_depart[Y0[i]] for i in indices2]

fig_bar2 = go.Figure()
fig_bar2.add_trace(go.Bar(x=X,
                y=Y,
                name='Availability',
                marker_color='rgb(26, 118, 255)',
                orientation='h'
                ))


fig_bar2.update_layout(
    #title='Saturation / Availability',
    #xaxis_tickfont_size=14,
    title='Avaibility',
    barmode='stack',
    xaxis={'categoryorder':'total descending'},
    yaxis=dict(
        autorange="reversed",
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    #barmode='group',
    bargap=0.05, # gap between bars of adjacent location coordinates.
    bargroupgap=0.05 # gap between bars of the same location coordinate.
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
                    html.P(['Date selection']),
                    dcc.DatePickerSingle(
                    id='date-picker-single',
                    date=dt(2020, 3, 25)
                        )
                ], className="three columns"),

                ########## DROPDOWN METRIC 1 ##########
                    html.Div(
                        [
                    html.Label(['Metric 1',
                    dcc.Dropdown(
                        id='metric_1',
                        options=metrics_dropdown,
                        style={
                            'width': '300px',
                            },
                        value='0')
                        ])
                    ], className="three columns"),

                ########## DROPDOWN METRIC 2 ##########
                    html.Div(
                [
                    html.Label(['Metric 2',
                    dcc.Dropdown(
                        id='metric_2',
                        options=metrics_dropdown,
                        style={
                            'width': '300px',
                            },
                        value='0'
                        )
                    ])
                ], className="three columns"),

                ########## DROPDOWN DEPARTMENT ##########
                    html.Div(
                [
                    html.Label(['Department',
                    dcc.Dropdown(
                        id='departments',
                        options=dep_dropdown,
                        style={
                            'width': '250px',
                            },
                        value=0
                        )
                        ])
                    ], className="three columns")

                ]),

                #************** GRAPHS ****************

                html.Div(
                [

                    ########## MAP ##########

                    html.Div([

                        dcc.Graph(id="map", figure=fig_map),

                        ], className="six columns"),

                    ########## TRENLINE ##########

                    html.Div([

                        html.Div([
                            dcc.Graph(id="trendline", figure=fig_trend)
                            ], className="row"),

                    ########## BAR CHART ##########

                        html.Div([
                                #children=[
                                html.Div([
                                        dcc.Graph(id='bar1',figure=fig_bar1),
                                        ], className="six columns"),
                                html.Div([
                                        dcc.Graph(id='bar2',figure=fig_bar2),
                                        ], className="six columns"),
                            ], className="row"),
                        ], className="six columns")
            ], className="twelve columns")
    ])

# ----------- CALLBACKS -------------------------

@app.callback(
    [dash.dependencies.Output('map', 'figure'),
    dash.dependencies.Output('bar1', 'figure'),
    dash.dependencies.Output('bar2', 'figure')],
    [dash.dependencies.Input('date-picker-single', 'date'),
     dash.dependencies.Input('metric_1', 'value'),
     dash.dependencies.Input('metric_2', 'value')])
def update_figure(selected_date, selected_metric, selected_metric_2):

    date = dt.strptime(re.split('T| ', selected_date)[0], '%Y-%m-%d')
    date_string = date.strftime('%Y-%m-%d')
    metric_name = metricName(int(selected_metric))
    metric_name_2 = metricName(int(selected_metric_2))

    if(metric_name == 'Medical staff saturation'):
        color_continuous_scale=[(0, "rgb(223, 30, 38)"), (0.02, "rgb(243, 114, 32)"),
                                            (0.9, "rgb(251, 163, 26)"), (1, "rgb(255, 213, 0)")]
    else:
        color_continuous_scale=None

    fig = px.choropleth(data_dict[metric_name], geojson=counties, color=date_string,
                    featureidkey="properties.code", locations="dep",
                    projection="mercator", hover_name="dep",
                    hover_data={
                                "dep":False,
                                date_string:False,
                                metric_name:(':.2f', data_dict[metric_name][date_string]),
                                metric_name_2:(':.2f', data_dict[metric_name_2][date_string])
                                },
                    color_continuous_scale=color_continuous_scale
                   )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=850)

    #####-----------------------update of chart bar1----------------------
    X0=list(data_dict[metric_name][date_string].values)
    Y0=list(data_dict[metric_name]['dep'].values)

    ## garder les 10 premieres valeures
    if(metric_name == 'Medical staff saturation'):
        indices1=lowest_indices(X0,10)
    else:
        indices1=Top_indices(X0,10)

    X=[int(X0[i]) for i in indices1]
    Y=[dict_depart[Y0[i]] for i in indices1]

    fig_bar1 = go.Figure()
    fig_bar1.add_trace(go.Bar(x=X,y=Y,
                    name="2020-03-18",
                    marker_color='rgb(55, 83, 109)',
                    orientation='h'
                    ))
    fig_bar1.update_layout(
        title='Saturation',
        barmode='stack',
        xaxis={'categoryorder':'total descending'},
        yaxis=dict(
            autorange="reversed",
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        bargap=0.05, # gap between bars of adjacent location coordinates.
        bargroupgap=0.05 # gap between bars of the same location coordinate.
    )

    #####-----------------------update of chart bar 2----------------------

    ## garder les 10 dernières valeures
    if(metric_name == 'Medical staff saturation'):
        indices2=Top_indices(X0,10)
    else:
        indices2=lowest_indices(X0,10)
    X=[int(X0[i]) for i in indices2]
    Y=[dict_depart[Y0[i]] for i in indices2]

    fig_bar2 = go.Figure()
    fig_bar2.add_trace(go.Bar(x=X,
                    y=Y,
                    name='Availability',
                    marker_color='rgb(26, 118, 255)',
                    orientation='h'
                    ))
    fig_bar2.update_layout(
        title='Avaibility',
        xaxis={'categoryorder':'total descending'},
        yaxis=dict(
            autorange="reversed",
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
        ),
        bargap=0.05, # gap between bars of adjacent location coordinates.
        bargroupgap=0.05 # gap between bars of the same location coordinate.
        )

    return fig, fig_bar1, fig_bar2

@app.callback(
    dash.dependencies.Output('trendline', 'figure'),
    [dash.dependencies.Input('metric_1', 'value'),
    dash.dependencies.Input('departments', 'value')])
def update_trendline(selected_metric, selected_department):
    metric_name = metricName(int(selected_metric))
    department_name = departmentNumber(selected_department)

    # Create figure
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter( x=data_dict[metric_name].columns[1:],
                        y=data_dict[metric_name][data_dict[metric_name]['dep']==department_name].values.flat[1:]))
    # Set title
    fig_trend.update_layout(
        title_text="Time series with range slider and selectors"
    )
    # Add range slider
    fig_trend.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([

                     dict(count=1,
                        label="day",
                        step="day",
                        stepmode="backward"),
                     dict(count=7,
                      label="week",
                      step="day",
                      stepmode="backward"),
                      dict(count=1,
                       label="1m",
                       step="month",
                       stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    return fig_trend




if __name__ == '__main__':
    app.run_server(port=8053,debug=True)
