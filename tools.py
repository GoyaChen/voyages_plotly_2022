from vars import *
import requests
import json
from app_secrets import *
from dash import dcc
import dash_bootstrap_components as dbc

#overwrite flatlabels w custom flatlabels enumerated above
r=requests.options(base_url+'voyage/?hierarchical=False',headers=headers)
md=json.loads(r.text)
for m in md2:
	md[m]['flatlabel']=md2[m]

def loadjson(fname):
	d=open(fname,"r")
	t=d.read()
	j=json.loads(t)
	d.close()
	return j
def dumpjson(fname,data):
	d=open(fname,"w")
	d.write(json.dumps(data))
	d.close()
	return True

def get_rangeslider(fq_varname,component_id):
	data={
		"aggregate_fields" : [fq_varname]
	}
	r=requests.post(url=base_url+"voyage/aggregations",headers=headers,data=data)
	j=json.loads(r.text)
	print(j)
	minval=j[fq_varname]['min']
	maxval=j[fq_varname]['max']
	component=dcc.RangeSlider(min=minval, max=maxval, marks=None, step=1, id=component_id, tooltip={"placement": "bottom", "always_visible": True})
	return component

def get_autocomplete_dropdown(component_id):
	
	component=dcc.Dropdown(id=component_id,multi=True,options=[],value=None)
	
	return component
	
def get_navlinks(registered_apps):
	navlinks=[]
	for ra in registered_apps:
		navlinks.append(dbc.NavLink(ra[1], href=ra[0], active="exact"))
	return navlinks		