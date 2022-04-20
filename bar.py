from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import re
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from bar_vars import *
from auth_settings import *
from authenticate import *

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

r=requests.options(base_url+'voyage/?hierarchical=False',headers=auth_headers)
md=json.loads(r.text)

url=base_url+'voyage/caches'
data={
	'cachename':'voyage_bar_and_donut_charts'
}

r=requests.post(url,data,headers=auth_headers)
j=r.text
df=pd.read_json(j)

app.layout = html.Div(children=[
	dcc.Graph(
		id='voyages-bar-graph',
		style={height="100%"}
	),
	html.Label('X variables'),
	dcc.Dropdown(
		id='x_var',
		options=[{'label':md[i]['flatlabel'],'value':i} for i in bar_x_vars],
		value=bar_x_vars[0],
		multi=False
	),
		html.Label('Y variables'),
	dcc.Dropdown(
		id='y_var',
		options=[{'label':md[i]['flatlabel'],'value':i} for i in bar_y_abs_vars],
		value=bar_y_abs_vars[0],
		multi=False
	),
	html.Label('Totals/Sums or Averages'),
	dcc.RadioItems(
				id='agg_mode',
				options=[{'label': i, 'value': i} for i in ['Totals/Sums','Averages']],
				value='Totals/Sums',
				labelStyle={'display': 'inline-block'}
			)
])

@app.callback(
	Output('voyages-bar-graph', 'figure'),
	Input('x_var', 'value'),
	Input('y_var', 'value'),
	Input('agg_mode','value')
	)

def update_figure(x_var,y_var,agg_mode):
	
	if agg_mode=='Averages':
		df2=df.groupby(x_var)[y_var].mean()
		df2=df2.reset_index()
	elif agg_mode=='Totals/Sums':
		df2=df.groupby(x_var)[y_var].sum()
		df2=df2.reset_index()
	
	yvarlabel=md[y_var]['flatlabel']
	xvarlabel=md[x_var]['flatlabel']
	
	fig=px.bar(df2,x=x_var,y=y_var,
		labels={
			y_var:yvarlabel,
			x_var:xvarlabel
			}
		)
	
	fig.update_layout(
		xaxis_title='',
		yaxis_title=''
	)

	return fig
	
if __name__ == '__main__':
	app.run_server(debug=True)