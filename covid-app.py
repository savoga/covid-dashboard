import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

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
                    # MAPBOX
            ], style={'columnCount': 2})
    ])

if __name__ == '__main__':
    app.run_server(debug=True)