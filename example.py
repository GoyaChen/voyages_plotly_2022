import plotly.express as px
from dash import Input, Output, callback, dash_table,State
import pandas as pd
import requests
import json
from app_secrets import *
import dash
import dash_core_components as dcc
import dash_html_components as html



donut_value_vars=[
	'voyage_dates__imp_length_home_to_disembark',
	'voyage_dates__length_middle_passage_days',	
	'voyage_ship__tonnage_mod',
	'voyage_crew__crew_voyage_outset',
	'voyage_crew__crew_first_landing',					
	'voyage_slaves_numbers__imp_total_num_slaves_embarked',
	'voyage_slaves_numbers__imp_total_num_slaves_disembarked',
	'voyage_slaves_numbers__imp_jamaican_cash_price'
]

donut_name_vars=[
	'voyage_ship__imputed_nationality__name',
	'voyage_ship__rig_of_vessel__name',
	'voyage_outcome__particular_outcome__name',
	'voyage_outcome__outcome_slaves__name',
	'voyage_outcome__outcome_owner__name',
	'voyage_outcome__vessel_captured_outcome__name',
	'voyage_outcome__resistance__name',
	'voyage_itinerary__imp_port_voyage_begin__place',
	'voyage_itinerary__imp_region_voyage_begin__region',
	'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
	'voyage_itinerary__imp_principal_region_of_slave_purchase__region',
	'voyage_itinerary__imp_principal_port_slave_dis__place',
	'voyage_itinerary__imp_principal_region_slave_dis__region',
	'voyage_itinerary__imp_broad_region_slave_dis__broad_region',
	'voyage_itinerary__place_voyage_ended__place',
	'voyage_itinerary__region_of_return__region'
	]

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(id='fizz'),
    dcc.Dropdown(
		id='donut_value_var',
		options=[i for i in donut_value_vars],
		value=donut_value_vars[0],
		multi=False
	),
	dcc.Dropdown(
		id='donut_sector_var',
		options=[i for i in donut_name_vars],
		value=donut_name_vars[0],
		multi=False
	),
])

@app.callback(
	Output('fizz', 'figure'),
	Input('donut_sector_var', 'value'),
	Input('donut_value_var', 'value'),
	)
def update_bar_graph(donut_sector_var,donut_value_var):
	global headers
	data={
		'selected_fields':[donut_sector_var,donut_value_var],
		'cachename':['voyage_bar_and_donut_charts']
	}
	
	url="https://voyages3-api.crc.rice.edu/voyage/caches"
	
	r=requests.post(url,data=data,headers=headers)
	j=r.text
	
	df=pd.read_json(j)
	fig = px.pie(df, values=donut_value_var, names=donut_sector_var)
	return fig



app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter







