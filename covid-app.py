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

# a modifier data_dict["taux_hosp"].set_index('dep')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ----------- MAP -----------
# pour visualiser lors du debugage sur python
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# dictionnaire des départements: code-->nom du département
df = pd.read_csv('data/departements-france.csv')
dict_depart={}
code=list(df['code_departement'].values)
nom=list(df['nom_departement'].values)
for i in range(len(df)):
    dict_depart[code[i]]=nom[i]


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

X=data_dict['taux_hosp'].columns
a=[0]
a.extend(savgol_filter(data_dict['taux_hosp'][data_dict['taux_hosp']['dep']=='01'].values[0][1:-1], 71, 3))
a.extend([0])
Y=a

fig_trend = px.line(data_dict['taux_hosp'], x=X,
                    y=Y,
                    title='Trend line')

# ----------- BAR CHART -----------

def Top_indices(liste,N):
    return sorted(range(len(liste)), key=lambda i: liste[i], reverse=True)[:N]

def lowest_indices(liste,N):
    return sorted(range(len(liste)), key=lambda i: liste[i], reverse=False)[:N]

X0=list(data_dict['taux_hosp']['2020-03-25'].values)
Y0=list(data_dict['taux_hosp']['dep'].values)

indices1=Top_indices(X0,10)

X=[int(X0[i]) for i in indices1]
Y=[dict_depart[Y0[i]]+" ("+Y0[i]+")" for i in indices1]

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
Y=[dict_depart[Y0[i]]+" ("+Y0[i]+")" for i in indices2]

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
                    #html.Button('-', id='buttonMinus'),
                    dcc.DatePickerSingle(
                    id='date-picker-single',
                    min_date_allowed=dt(2020, 3, 18),
                    max_date_allowed=dt(2020, 6, 16),
                    style={
                        'width': '250px',
                        },
                    date=dt(2020, 3, 25)

                        )

                    #,
                    #html.Button('+', id='buttonPlus'),

                ], className="three columns"),

                ########## DROPDOWN METRIC 2 ##########

                    html.Div(
                    [
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=dt(2020, 3, 18),
                            max_date_allowed=dt(2020, 6, 16),
                            initial_visible_month=dt(2020, 3, 18),
                            end_date=dt(2020, 6, 16).date(),

                        ),

                        html.Div(id='output-container-date-picker-range')

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



                ######### DROPDOWN DEPARTMENT ##########
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

                        ], className="six columns"),

                    ########## TRENLINE ##########

                    html.Div([

                        html.Div([
                            dcc.Graph(id="trend",figure=fig_trend)
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
    dash.dependencies.Output('trend', 'figure'),
    dash.dependencies.Output('bar1', 'figure'),
    dash.dependencies.Output('bar2', 'figure')],
    [dash.dependencies.Input('date-picker-single', 'date'),
     dash.dependencies.Input('metric_1', 'value'),
     dash.dependencies.Input('departments', 'value')])
def update_figure(selected_date, selected_metric,selected_department):
    date = dt.strptime(re.split('T| ', selected_date)[0], '%Y-%m-%d')
    date_string = date.strftime('%Y-%m-%d')
    metric_name = metricName(int(selected_metric))


#---------------------update of map -----------------------------

    fig = px.choropleth(data_dict[metric_name], geojson=counties, color=date_string,
                    locations="dep", featureidkey="properties.code",
                    projection="mercator", labels={'02/01/2020':'saturation'},
                    #color_continuous_scale=[(0, "rgb(223, 30, 38)"),(0.02, "rgb(243, 114, 32)"),
                    #                        (0.2, "rgb(223, 70, 38)"),(0.4, "rgb(243, 184, 32)"),
                    #                        (0.9, "rgb(251, 163, 26)"), (1, "rgb(255, 213, 0)")]
                    color_continuous_scale=[(0, "rgb(0, 0, 0)"),(0.02, "rgb(210, 0, 0)")]#,
                                            #(0.2, "rgb(170, 0, 0)"),(0.4, "rgb(120, 0, 0)"),
                                            #(0.2, "rgb(80, 0, 0)"),(0.4, "rgb(50, 0, 0)"),
                                            #(0.9, "rgb(20, 0, 0)"), (1, "rgb(5, 0, 0)")]
                   )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=900) #plot_bgcolor='#1e1e1e',paper_bgcolor='#1e1e1e'


#---------------------update of trend-----------------------------

    department=str(selected_department)[:2]
    print(date_string)
    X=data_dict[metric_name].columns
    a=[0]
    a.extend(savgol_filter(data_dict[metric_name][data_dict[metric_name]['dep']==department].values[0][1:-1], 71, 5))
    a.extend([0])
    Y=a
    fig_trend2 = px.line(data_dict[metric_name], x=X,
                        y=Y,
                        title='Trend line')#,paper_bgcolor='#1e1e1e')
    #fig_trend2.update_layout(plot_bgcolor='#1e1e1e',paper_bgcolor='#1e1e1e')

#---------------------update of chart bar-----------------------------

#####-----------------------update of chart bar1----------------------
    print(date_string)
    X0=list(data_dict[metric_name][date_string].values)
    Y0=list(data_dict[metric_name]['dep'].values)

## garder les 10 premieres valeures
    indices1=Top_indices(X0,10)
    X=[int(X0[i]) for i in indices1]
    Y=[dict_depart[Y0[i]]+" ("+Y0[i]+")" for i in indices1]

    fig_bar1 = go.Figure()
    fig_bar1.add_trace(go.Bar(x=X,y=Y,
                    name="2020-03-18",
                    marker_color='rgb(55, 83, 109)',
                    orientation='h'
                    ))
    fig_bar1.update_layout(
        title='Saturation',
        barmode='stack',
        #plot_bgcolor="#1e1e1e",
        #paper_bgcolor="#1e1e1e",
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
    indices2=lowest_indices(X0,10)
    X=[int(X0[i]) for i in indices2]
    Y=[dict_depart[Y0[i]]+" ("+Y0[i]+")" for i in indices2]

    fig_bar2 = go.Figure()
    fig_bar2.add_trace(go.Bar(x=X,
                    y=Y,
                    name='Availability',
                    marker_color='rgb(26, 118, 255)',
                    orientation='h'
                    ))
    fig_bar2.update_layout(
        title='Avaibility',
        #barmode='stack',
        xaxis={'categoryorder':'total descending'},
        #plot_bgcolor='#1e1e1e',
        #paper_bgcolor='#1e1e1e',
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
        bargap=0.05, # gap between bars of adjacent location coordinates.
        bargroupgap=0.05 # gap between bars of the same location coordinate.
)
    return fig,fig_trend2,fig_bar1,fig_bar2

@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
        #string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '

    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

        A=data_dict["taux_hosp"].drop('sheet',axis=1)
        A.set_index('dep')
        A
        A=A.set_index('dep')
        A
        df=A;df.columns = pd.to_datetime(df.columns)
        df
        df.columns
        df['2020-03-18':'2020-03-119']
        df['2020-03-18':'2020-03-20']
        df.loc[:,'2020-03-18':'2020-03-20']
        #string_prefix = string_prefix + 'End Date: ' + end_date_string
    #if len(string_prefix) == len('You have selected: '):
    #    return 'Select a date to see it displayed here'
    #else:
    #    return string_prefix





if __name__ == '__main__':
    app.run_server(port=8053,debug=True)
