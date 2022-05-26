from dash import dcc, html,dash_table
from vars import *
import dash_bootstrap_components as dbc
import requests
import json
import time
import dash_leaflet as dl
from app_secrets import *
from tools import *

#token validation
detail=md.get('detail')
if detail == "Invalid token.":
	print("**************\n%s\n%s\nSERVER REJECTED AUTH TOKEN -- CHECK YOUR SETTINGS\n**************" %(base_url,headers))
	time.sleep(15)
	exit()

bar_layout = dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div(
					[					
						dbc.Card(
							[dbc.Row(
								[
									dbc.Col(
											html.Div([
												html.Label('X variables'),
												dcc.Dropdown(
													id='bar_x_var',
													options=[{'label':md[i]['flatlabel'],'value':i} for i in bar_x_vars],
													value=bar_x_vars[0],
													multi=False
												)
											]),						
											width=12,xs=12,sm=12,md=12,lg=6
										),
										dbc.Col(
											html.Div([
												html.Label('Y variables'),
												dcc.Dropdown(
													id='bar_y_var',
													options=[{'label':md[i]['flatlabel'],'value':i} for i in bar_y_abs_vars],
													value=bar_y_abs_vars[0],
													multi=False
												),
												html.Br(),
												html.Label('Totals/Sums or Averages'),
												dcc.RadioItems(
													id='bar_agg_mode',
													options=[{'label': i, 'value': i} for i in ['Totals/Sums','Averages']],
													value='Totals/Sums',
													labelStyle={'display': 'inline'}
												)
											]),
											width=12,xs=12,sm=12,md=12,lg=6
										)
								]
							)]
						)
					]
				)
			),
		]),
		dbc.Row([
			dbc.Col(
				html.Div(
					[dcc.Graph(id='voyages-bar-graph')]
				),
			),
		]),
	],
	style={"height": "100vh"},
)

xyscatter_layout =  dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div([
					dbc.Card(
						[dbc.Row([
							dbc.Col(
									html.Div([
										html.Label('X variables'),
										dcc.Dropdown(
											id='scatter_x_vars',
											options=[{'label':md[i]['flatlabel'],'value':i} for i in scatter_plot_x_vars],
											value=scatter_plot_x_vars[0],
											multi=False
										),
									]),						
									width=9,xs=12,sm=12,md=9,lg=9
							),
							dbc.Col(
								html.Div([
									html.Label('Totals/Sums or Averages'),
									dcc.RadioItems(
												id='scatter_agg_mode',
												options=[{'label': i, 'value': i} for i in ['Totals/Sums','Averages']],
												value='Totals/Sums',
												labelStyle={'display': 'block'}
									)
								]),width=3,xs=12,sm=12,md=3,lg=3)
						]),
						dbc.Row([
							dbc.Col([
								html.Div([
									html.Label('Y variables'),
									dcc.Dropdown(
										id='scatter_y_vars',
										options=[{'label':md[i]['flatlabel'],'value':i} for i in scatter_plot_y_vars],
										value=scatter_plot_y_vars[0],
										multi=False
									)
								])
							],width=12),
						]),
						dbc.Row([
							dbc.Col([
								html.Label('Group By'),
								dcc.Dropdown(
									id='scatter_factors',
									options= [{'label':md[i]['flatlabel'],'value':i} for i in scatter_plot_factors] + [{"label":"Do Not Group","value":"Do Not Group"}],
									value="Do Not Group",
									multi=False
								)
							],width=12)
						]),
						dbc.Row([
							dbc.Col(
								html.Div(
									[dcc.Graph(id='voyages-scatter-graph')]
								),
							),
						])
					]
				)
			])
		)
	])
	]
)


donut_layout =  dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div([
					dbc.Card(
						[dbc.Row(
							[
								dbc.Col(
										html.Div([
											html.Label('Sectors'),
											dcc.Dropdown(
												id='donut_sector_var',
												options=[{'label':md[i]['flatlabel'],'value':i} for i in donut_name_vars],
												value=donut_name_vars[0],
												multi=False
											),
										]),
										width=12,xs=12,sm=12,md=12,lg=6
									),
									dbc.Col(
										html.Div([
											html.Label('Values'),
											dcc.Dropdown(
												id='donut_value_var',
												options=[{'label':md[i]['flatlabel'],'value':i} for i in donut_value_vars],
												value=donut_value_vars[0],
												multi=False
											),
											html.Br(),
											html.Label('Aggregation'),
											dcc.RadioItems(
												id='donut_agg_mode',
												options=[{'label': i, 'value': i} for i in ['Totals/Sums','Averages']],
												value='Totals/Sums',
												labelStyle={'display': 'inline'}
											)
										]),
										width=12,xs=12,sm=12,md=12,lg=6
									)
							]
						)]
					)
				])
			),
		]),
		dbc.Row([
			dbc.Col(
				html.Div(
					[dcc.Graph(id='voyages-donut-graph')]
				),
			),
		])
	]
)




pivot_table_layout =  dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div([
					dbc.Card(
						[dbc.Row(
							[
								dbc.Col(
										html.Div([
											html.Label('Rows'),
											dcc.Dropdown(
												id='rows',
												options=[{'label':md[i]['flatlabel'],'value':i} for i in pivot_table_categorical_vars],
												value=pivot_table_categorical_vars[0],
												multi=False
											),
											html.Label('Columns'),
											dcc.Dropdown(
												id='columns',
												options=[{'label':md[i]['flatlabel'],'value':i} for i in pivot_table_categorical_vars],
												value=pivot_table_categorical_vars[1],
												multi=False
											),
											html.Label('Cells'),
											dcc.Dropdown(
												id='cells',
												options=[{'label':md[i]['flatlabel'],'value':i} for i in pivot_table_numerical_vars],
												value=pivot_table_numerical_vars[0],
												multi=False
											),
											html.Label('Remove NA?'),
											dcc.RadioItems(
												id='rmna',
												options=[{'label': i, 'value': i} for i in ['True','False']],
												value='sum',
												labelStyle={'display': 'inline'}
											),
											html.Label('Value Function'),
											dcc.RadioItems(
												id='valuefunction',
												options=[{'label': i, 'value': i} for i in ['sum','mean','normalize_columns','normalize_rows']],
												value='sum',
												labelStyle={'display': 'inline'}
											)
										]),
									)
							]
						)]
					)
				])
			),
		]),
		dbc.Row([
			dbc.Col(
				html.Div(
					[dash_table.DataTable(id='voyages-pivot-table')]
				),
			),
		])
	]
)

data_table =  dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div([
					"Show columns (\"*\" denotes imputed variables):",
					dcc.Dropdown(
						id="table-colselect",
						multi=True,
						options=[{'label':md[i]['flatlabel'],'value':i} for i in voyage_export_vars],
						value=[i for i in voyage_table_default_vars]
					),
				]),
			)
		]),
		dbc.Row([
			dbc.Col(
				dash_table.DataTable(
					id='table-multicol-sorting',
					columns=[],
					page_current=0,
					page_size=20,
					page_action='custom',
					sort_action='custom',
					sort_mode='single',
					style_cell={
						'height': 'auto',
						# all three widths are needed
						'width': '100px', 'maxWidth': '180px',
						'whiteSpace': 'normal'
					}
				)
			)
		])
	]
)



leaflet_map =  dbc.Container(
	[
		dbc.Row([
			dbc.Col(
				html.Div([
					html.Label('Map style'),
					dcc.Dropdown(
						id='leaflet-map-tilesets-select',
						options=[i for i in map_tilesets],
						value=map_tilesets[0]['value'],
						multi=False
					)
				])
			)
		]),
		dbc.Row([
			dbc.Col(
				html.Div([
					dl.Map(
						[
							dl.TileLayer(id="tile-layer"),
							dl.LayerGroup(id='routes-feature-layer'),
						],
						id="map",
						style={
							'width': '100%',
							'height': '100vh',
							'margin': "auto",
							"display": "block"
						},
						center=(0,0),
						zoom=2
					)
				])
			)
		])
	]
)

search_pane = dbc.Card([
		html.H5("Search/Filters"),
		dbc.Row([
			dbc.Col([
				html.Div([
					html.Label('Select Dataset'),
					dcc.RadioItems(
						id='dataset-radio',
						options=[{'label': i[0], 'value': i[1]} for i in 
								[
									["Trans-Atlantic",0],
									["Intra-American",1]
								]
							],
						value=0,
						labelStyle={'display': 'block'}
					)
				])
			],width=5),
			dbc.Col([html.Div([html.P('')])],width=5),
			dbc.Col([
				html.Div([
					html.Label('Results Count:'),
					html.P(id="search_pane_results_count")
				])
			],width=2)
		]),
		dbc.Row([
			html.Hr(),
			html.H6("Autocomplete Search"),
			dbc.Row([
				dbc.Col(
					html.Div([
						html.Label('Select text field to filter on'),
						dcc.Dropdown(
							id="autocomplete-field-selector",
							multi=False,
							options=[{'label':md[i]['flatlabel'],'value':i} for i in autocomplete_text_fields],
							value=autocomplete_text_fields[0]
						),
						html.Label('Search for text field values'),
						html.Div([
							get_autocomplete_dropdown('my-multi-dynamic-dropdown')
						],id="autocomplete-text-div"),
						html.Br()
					]),
				)
			])
		]),
		dbc.Row([
			html.Hr(),
			dbc.Col(
				html.Div([
					html.H6("Numeric Range Search"),
					html.Label('Select numeric field to filter on'),
					html.Div([
						dcc.Dropdown(
							id="rangeslider-field-selector",
							multi=False,
							options=[{'label':md[i]['flatlabel'],'value':i} for i in rangeslider_numeric_fields],
							value=rangeslider_numeric_fields[0]
						),
					]),
					html.Div([
						get_rangeslider(rangeslider_numeric_fields[0],'rangeslider-numeric-fields')
					],id="rangeslider-numeric-div")
				]),width=12
			)
		])
	])



