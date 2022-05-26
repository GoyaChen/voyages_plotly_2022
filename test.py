import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback
from app_secrets import headers
import requests
import pandas as pd
base_url = 'https://voyages3-api.crc.rice.edu/voyage/'

app = dash.Dash()

"""
These arrays provide the variety of variables which can be used for the construction of the data visualizations.
Numeric_vars referred to the actual value we are trying to retrieve, geo_vars refer to variables indicating location
and the date_vars provide time references against which the data would be queried. 
"""
numeric_vars = ['voyage_slaves_numbers__imp_total_num_slaves_disembarked',
                'voyage_slaves_numbers__imp_total_num_slaves_embarked']

geo_vars = ['voyage_itinerary__imp_principal_place_of_slave_purchase__place',
            'voyage_itinerary__imp_principal_port_slave_dis__place',
            'voyage_itinerary__imp_principal_region_slave_dis__region',
            'voyage_itinerary__imp_principal_region_of_slave_purchase__region']

date_vars = ['voyage_dates__arrival_at_second_place_landing_yyyy',
             'voyage_dates__date_departed_africa_yyyy',
             'voyage_dates__first_dis_of_slaves_yyyy',
             'voyage_dates__imp_arrival_at_port_of_dis_yyyy',
             'voyage_dates__imp_departed_africa_yyyy',
             'voyage_dates__imp_voyage_began_yyyy',
             'voyage_dates__slave_purchase_began_yyyy',
             'voyage_dates__third_dis_of_slaves_yyyy',
             'voyage_dates__vessel_left_port_yyyy',
             'voyage_dates__voyage_began_yyyy',
             'voyage_dates__voyage_completed_yyyy']

r = requests.options(base_url + '?hierarchical=False', headers=headers)  # to get the specific label names of above vars
drop_dict = r.json()
geo_drop = [drop_dict[i]['flatlabel'] for i in geo_vars]
numeric_drop = [drop_dict[i]['label'] for i in numeric_vars]
date_drop = [drop_dict[i]['label'] for i in date_vars]

app.layout = dbc.Container([
    dbc.Row([
        html.Label('geo var'),
        dcc.Dropdown(
            id='geo_var',
            options=geo_drop,
            value=geo_vars[0],
            multi=False
        )
    ]),
    dbc.Row([
        html.Label('numeric var (y var)'),
        dcc.Dropdown(
            id='numeric_var',
            options=numeric_drop,
            value=numeric_vars[0],
            multi=False
        )
    ]),
    dbc.Row([
        html.Label('date var (x var)'),
        dcc.Dropdown(
            id='date_var',
            options=date_drop,
            value=date_vars[0],
            multi=False
        )
    ]),
    dbc.Row([
        html.Div(
            [dcc.Graph(id='voyages-bar-graph')]
        ),
    ]),
])

@callback(
    Output('voyages-bar-graph', 'figure'),
    Input('geo_var', 'value'),
    Input('numeric_var', 'value'),
    Input('date_var', 'value'),
)
def update_bar_graph(geo_var, numeric_var, date_var):
    print(geo_var)
    print(numeric_var)
    print(date_var)

    x_var = date_vars[date_drop.index(date_var)]
    y_var = numeric_vars[numeric_drop.index(numeric_var)]
    color_var = geo_vars[geo_drop.index(geo_var)]
    print("x: ",x_var)
    print("y: ", y_var)
    print("color: ", color_var)
    data = {"selected_fields": [x_var, y_var, color_var]}
    url = base_url + 'dataframes'
    r = requests.post(url, headers=headers, data=data)
    j = r.text
    df = pd.read_json(j)
    df = df.dropna()
    print(df)
    fig = px.bar(df, x=x_var, y=y_var, color=color_var)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
