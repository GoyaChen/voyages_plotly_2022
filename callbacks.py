from dash import Input, Output, callback, dash_table,State
from dash.exceptions import PreventUpdate
import pandas as pd
import re
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import gc
from app_secrets import *
from tools import *
import dash_leaflet as dl


def update_df(url,data):
	global headers
	r=requests.post(url,data=data,headers=headers)
	j=r.text
	
	try:
		results_count=r.headers['results_count']
	except:
		results_count=None
	df=pd.read_json(j)
	return df,results_count


def labeltrim(s,threshold=15):
	if len(s)>threshold:
		s=s[:threshold-1]+"..."
	return s


@callback(
	Output('voyages-bar-graph', 'figure'),
	Input('bar_x_var', 'value'),
	Input('bar_y_var', 'value'),
	Input('bar_agg_mode','value'),
	Input('search_params', 'data')
	)
def update_bar_graph(x_var,y_var,agg_mode,search_data):
	global md

	data={
		'selected_fields':[x_var,y_var],
		'cachename':['voyage_bar_and_donut_charts']
	}
	
	search_data=json.loads(search_data)
	for sdk in search_data:
		data[sdk]=search_data[sdk]
	
	df,results_count=update_df(
		base_url+'voyage/caches',
		data=data
	)
	
	print(df)
	
	if agg_mode=='Averages':
		df2=df.groupby(x_var)[y_var].mean()
		df2=df2.reset_index()
	elif agg_mode=='Totals/Sums':
		df2=df.groupby(x_var)[y_var].sum()
		df2=df2.reset_index()
	
	print(df2)
	
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
		yaxis_title='',
		height=700
	)
	del df2, df
	gc.collect()
	return fig

@callback(
	Output('voyages-scatter-graph', 'figure'),
	Input('scatter_agg_mode', 'value'),
	Input('scatter_x_vars', 'value'),
	Input('scatter_y_vars', 'value'),
	Input('scatter_factors', 'value'),
	Input('search_params', 'data')
	)

def update_scatter_graph(agg_mode,x_val,y_val,color_val,search_data):
	global md
	def agg_functions(x_val,y_val,agg_mode,df3):
		if agg_mode=='Averages':
			df3=df3.groupby(x_val)[y_val].mean()
			df3=df3.reset_index()
		elif agg_mode=='Totals/Sums':
			df3=df3.groupby(x_val)[y_val].sum()
			df3=df3.reset_index()
		return(df3)
	
	selected_fields=[i for i in [x_val,y_val,color_val] if i!="Do Not Group"]
	
	data={
		'selected_fields':selected_fields,
		'cachename':['voyage_xyscatter']
	}
	
	search_data=json.loads(search_data)
	for sdk in search_data:
		data[sdk]=search_data[sdk]
	
	df,results_count=update_df(
		base_url+'voyage/caches',
		data=data
	)
	
	figtitle='Stacked %s of:<br>' %agg_mode.lower() + md[y_val]['flatlabel']
	
	fig=go.Figure()	
	
	if color_val!="Do Not Group":
		colors=df[color_val].unique()
		for color in colors:
			df2=df[df[color_val]==color]
			df2=agg_functions(x_val,y_val,agg_mode,df2)
			x_vals=df2[x_val]
			y_vals=df2[y_val]
			trace_name=color
	
			fig.add_trace(go.Scatter(
				x=x_vals,
				y=y_vals,
				name=trace_name,
				stackgroup='one',
				line= {'shape': 'spline'},
				mode='none')
			)
	else:
		df2=agg_functions(x_val,y_val,agg_mode,df)
		x_vals=df2[x_val].values
		y_vals=df2[y_val].values
		fig.add_trace(go.Scatter(
			x=x_vals,
			y=y_vals,
			fill='tozeroy')
		)
	df3=None
	df2=None
	del df,df2,df3
	gc.collect()
	fig.update_layout(height=700)
	
	return fig

@callback(
	Output('voyages-donut-graph', 'figure'),
	Input('donut_sector_var', 'value'),
	Input('donut_value_var', 'value'),
	Input('donut_agg_mode','value'),
	Input('search_params', 'data')
	)
def donut_update_figure(sector_var,value_var,agg_mode,search_data):
	global md
	
	data={
		'selected_fields':[sector_var,value_var],
		'cachename':['voyage_bar_and_donut_charts']
	}
	
	search_data=json.loads(search_data)
	for sdk in search_data:
		data[sdk]=search_data[sdk]
	
	df,results_count=update_df(
		base_url+'voyage/caches',
		data=data
	)
	
	if agg_mode=='Averages':
		df2=df.groupby(sector_var)[value_var].mean()
		df2=df2.reset_index()
	elif agg_mode=='Totals/Sums':
		df2=df.groupby(sector_var)[value_var].sum()
		df2=df2.reset_index()
	sectorvarlabel=md[sector_var]['flatlabel']
	valuevarlabel=md[value_var]['flatlabel']
	fig=px.pie(df2,values=value_var,names=sector_var,
		labels={
			sector_var:sectorvarlabel,
			value_var:valuevarlabel
			},
		hole=.4
		)
	fig.update_layout(height=700)
	fig.update_traces(textposition='inside', textinfo='percent+label')
	del df,df2
	gc.collect()
	return fig

@callback(
	Output('voyages-pivot-table', 'data'),
	Input('rows', 'value'),
	Input('columns', 'value'),
	Input('cells','value'),
	Input('rmna','value'),
	Input('valuefunction','value'),
	Input('search_params', 'data')
	)
def pivot_table_update_figure(rows,columns,cells,rmna,valuefunction,search_data):
	global md
	
	search_data=json.loads(search_data)
	
	normalize=False
	if valuefunction=="normalize_columns":
		normalize="columns"
		valuefunction="sum"
	elif valuefunction=="normalize_rows":
		normalize="index"
		valuefunction="sum"
	
	data={
		'rmna':[rmna],
		'normalize':[normalize],
		'groupby_fields':[rows,columns],
		'value_field_tuple':[cells,valuefunction],
		'cachename':['voyage_pivot_tables']
	}

	for sdk in search_data:
		data[sdk]=search_data[sdk]

	df,results_count=update_df(
		base_url+'voyage/groupby',
		data=data
	)
	
	
	
	if normalize != False:
		df=df*100
		df=df.round(1)
	elif valuefunction=="mean":
		df=df.round(0)
	
	df=df.rename_axis('').reset_index()
	
	df=df.fillna(0)
	
	output=df.to_dict('records')
	
	return output

#per:
##https://voyages-leaflet.herokuapp.com/
##https://github.com/JohnMulligan/voyages-api-leaflet
##https://dash-leaflet.herokuapp.com/

@callback(
	Output('tile-layer', 'url'),
	Input('leaflet-map-tilesets-select','value')
	)
def get_leaflet_tiles(tileset_select):
	return tileset_select

import voyages_geo_to_geojson_points_dict as vd
gd=vd.main()




@callback(
    Output('table-multicol-sorting', "data"),
    Output('table-multicol-sorting',"columns"),
    Output('table-multicol-sorting',"page_count"),
    Input('table-multicol-sorting', "page_current"),
    Input('search_params', 'data'),
	Input('table-colselect','value'),
	Input('table-multicol-sorting','sort_by')
)
def update_table(page_current,search_data,colnames,sort_by):
	if colnames == []:
		raise PreventUpdate
	
	else:
		global md
		
		results_per_page=20
		
		columns=[{"name": md[i]['flatlabel'], "id": i} for i in colnames]
	
		data={
			'selected_fields':colnames,
			'cachename':['voyage_export'],
			'results_per_page':[results_per_page],
			'results_page':[page_current+1]
		}
		sort_params=[]
		if sort_by is not None:
			for sb in sort_by:
				direction=sb['direction']
				colname=sb['column_id']
				sign={'asc':'','desc':'-'}[direction]
				sort_params.append(sign+colname)
		data['order_by']=sort_params

		search_data=json.loads(search_data)
		for sdk in search_data:
			data[sdk]=search_data[sdk]

		df,results_count=update_df(
			base_url+'voyage/caches',
			data=data
		)
		
		results_count=int(results_count)
		results_per_page=int(results_per_page)
		
		page_count_int=int(results_count/results_per_page)

		page_count_mod=results_count%results_per_page
		
		if page_count_mod !=0:
			page_count_int+=1
	
		return df.to_dict('records'),columns,page_count_int

@callback(
	Output('routes-feature-layer', 'children'),
	Input('search_params', 'data')
	)
def get_leaflet_routes(search_data):
	global gd
	global md
	
	search_data=json.loads(search_data)
	
	#with routes, the way those networks are currently built, we can really only do ports...
	##Specifically,
	###A) the port_routes json tables are keyed against the sql id not the spss value (why?)
	###B) the regional_routes json appears to be keyed to NOTHING in the db
	##That all needs to be changed: spss values, and everything in the db.
	
	groupby_fields=[
		'voyage_itinerary__imp_principal_port_slave_dis__id',
		'voyage_itinerary__imp_principal_place_of_slave_purchase__id'
		]
	datasetnamemap={0:"trans",1:"intra"}
	
	#load the appropriate routes (different for transatlantic vs intraamerican)
	port_routes=loadjson(os.path.join('static',datasetnamemap[search_data['dataset'][0]],'port_routes.json'))
	regional_routes=loadjson(os.path.join('static',datasetnamemap[search_data['dataset'][0]],'regional_routes.json'))
	
	data={
		'groupby_fields':groupby_fields,
		'value_field_tuple':['voyage_slaves_numbers__imp_total_num_slaves_embarked','sum'],
		'cachename':['voyage_maps'],
		'rmna':['All']
	}
	
	for sdk in search_data:
		data[sdk]=search_data[sdk]
	
	
	##ONLY LOCATIONS THAT SHOULD BE SHOWN ON THE MAP
	for groupby_field in groupby_fields:
		groupbyfield_showonmap_varname=re.sub("__id$","__show_on_map",groupby_field)
		data[groupbyfield_showonmap_varname]=["True"]
	
	r=requests.post(url=base_url+'voyage/groupby',headers=headers,data=data)
	j=json.loads(r.text)
	
	routes_featurecollection={"type":"FeatureCollection","features":[]}
	
	for source in j:
		for target in j[source]:
			sv=int(eval(source))
			tv=int(eval(target))
			
			#this will fail if there's no lookup for the given port's pk in the json
			s_reg=str(port_routes['src'][str(sv)]['reg'])
			t_reg=str(port_routes['dst'][str(tv)]['reg'])
			
			if s_reg=="-1" or t_reg=="-1":
				skipthis=True
			else:
				skipthis=False
			
			if not skipthis:
				s_lon,s_lat=gd[sv]['geometry']['coordinates']
				t_lon,t_lat=gd[tv]['geometry']['coordinates']
				
				#try to use the routing, but draw a straight line if there is none
				try:
					region_linestring=[[i[1],i[0]] for i in regional_routes[str(s_reg)][str(t_reg)]]
					linestring=[[s_lon,s_lat]]+region_linestring+[[t_lon,t_lat]]
				except:
					linestring=[[s_lon,s_lat],[t_lon,t_lat]]
				
				v=j[source][target]
				if v>0:
					sname=gd[sv]['properties']['name']
					tname=gd[tv]['properties']['name']
					text="%s people transported from %s to %s" %(int(v),sname,tname)
					label="%s --> %s" %(labeltrim(sname),labeltrim(tname))
					routes_featurecollection['features'].append({
						"type":"Feature",
						"geometry":{
							"type":"LineString",
							"coordinates":linestring
						},
						"properties":{
							"Value":np.log(v),
							"source_id":sv,
							"target_id":tv,
							"label":label
						}
					})
		
	#dumpjson("routes_featurecollection.json",routes_featurecollection)
	
	return dl.GeoJSON(data=routes_featurecollection)

##THIS TRANSLATES THE SEARCH INTERFACE COMPONENTS INTO A JSON QUERY OBJECT
##WHICH WE WILL PASS INTO OUR DASHBOARD QUERIES
@callback(
	Output('search_params', 'data'),
	Output('search_pane_results_count','children'),
	Input('dataset-radio','value'),
	Input('rangeslider-field-selector','value'),
	Input('rangeslider-numeric-fields','value'),
	Input('my-multi-dynamic-dropdown','value'),
	Input("autocomplete-field-selector","value")
	)
def update_search_params(dataset,rangeslider_field_name,rangeslider_range,autocomplete_values,autocomplete_field_name):
	
	search_params={}
	
	search_params[rangeslider_field_name]=rangeslider_range
	search_params[autocomplete_field_name]=autocomplete_values
	
	dataset=[dataset,dataset]
	search_params['dataset']=dataset
	
	#maybe this should be improved ...
	##currently one does currently need to specify a cache if you're going to hit the cache endpoint
	##so here i'm arbitrarily using the bar + donut chart
	data={
		'selected_fields':[rangeslider_field_name],
		'cachename':['voyage_bar_and_donut_charts'],	
	}
	for sdk in search_params:
		data[sdk]=search_params[sdk]
	
	df,results_count=update_df(
		base_url+'voyage/caches',
		data=data
	)
	
	return json.dumps(search_params),results_count


@callback(
    Output("rangeslider-numeric-div", "children"),
	[Input("rangeslider-field-selector", "value")]
)
def update_multi_options(rangeslider_field_name):
	
	return get_rangeslider(rangeslider_field_name,'rangeslider-numeric-fields')

#clear values
@callback(
    Output("my-multi-dynamic-dropdown", "value"),
    
	[Input("autocomplete-field-selector", "value")]
)
def update_multi_options(autocomplete_field_name):
	
	return []


#from https://dash.plotly.com/dash-core-components/dropdown
@callback(
    Output("my-multi-dynamic-dropdown", "options"),
	[Input("my-multi-dynamic-dropdown", "search_value"),
	Input("autocomplete-field-selector","value"),
	State("my-multi-dynamic-dropdown", "value")]
)
def autocompletion(search_value, field_name,state_value):
	
	#only going to work with a single field for now
	varname=field_name
	data={varname: [search_value] if search_value else ['']}
	r=requests.post(url=base_url+'voyage/autocomplete',headers=headers,data=data)
	#print(r.text)
	j=json.loads(r.text)
	autocomplete_results=[
		{"label":i,"value":i} for i in j[varname]
	]
	
	if type(state_value)==list:
		autocomplete_results+=[{"label":i,"value":i} for i in state_value]
	elif type(state_value)==str:
		autocomplete_results+=[{"label":i,"value":i} for i in [state_value]]
	
	return autocomplete_results

