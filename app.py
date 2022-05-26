from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from layouts import *
from vars import *
import requests
import re
from callbacks import *
import time
import json
from app_secrets import *
from tools import *

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
server = app.server

registered_apps=[
	["data_table","Data Table"],
	["xyscatter_layout","Scatter and Timeline Graphs"],
	["bar_layout","Bar Charts"],
	["donut_layout","Donut Charts"],
	["pivot_table_layout","Pivot Table Layout"],
	["leaflet_map","Leaflet map (experimental)"],
	["test_graph","test graph"]
]

data_canada = px.data.gapminder().query("country == 'Canada'")
fig = px.bar(data_canada, x='year', y='pop')

app.layout =  dbc.Container(
	[	
		dcc.Store(id="search_params"),
		dcc.Location(id="url"),
		dbc.Row([
			dbc.Col(
				get_navlinks(registered_apps),
				width=2,xs=12,sm=12,md=2,lg=2,
				style={"background-color": "#f8f9fa"}
				
			),
			dbc.Col([
				dbc.Row([
					search_pane
				]),
				html.Hr(),
				dbc.Row([
					dbc.Col(
						html.Div(id='page-content'),
					)
				])
			], width=10,xs=12,sm=12,md=10,lg=10)
		]),
			
	],fluid=True
)

@app.callback(
	Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(selected_app_layout_name):
	
	selected_app_layout_name=re.sub("/","",selected_app_layout_name)
	
	if selected_app_layout_name not in [k[0] for k in registered_apps]:
		selected_app_layout_name=registered_apps[0][0]
	
	return eval(selected_app_layout_name)


if __name__ == '__main__':
    app.run_server(debug=True)