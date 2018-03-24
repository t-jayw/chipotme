import re, sys, dash
import pandas as pd
import requests as r
import zipcodes as zc
import matplotlib.pyplot as plt
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import statsmodels.api as sm

from plotly.graph_objs import *
from bs4 import BeautifulSoup as bs
from dash.dependencies import Input, Output
from textwrap import dedent as d

import LineGraph as lg

import StoreLocator as sl
import new_DataModel as dm
import GeoScatter as gs 
import HeatMap as hm
import MapBox as mb 
# 

# Load data
data_obj = dm.DataHandler()

df = data_obj.final_df

geo = gs.GeoScatter(df)
heat = hm.HeatMap(df)
box = mb.MapBox(df)

app = dash.Dash()

app.layout  = html.Div([

html.Div([
	html.H1('chipot.me',), 
	html.P("""Analysis of your Chipotle consumption from mint.com transaction history""",)
]),

## SPEND LINE
html.Div([
	html.Div(
  		[lg.spendline_radio,
  		dcc.Markdown('''Forecast Future Values[*](https://xkcd.com/605/)'''),
  		lg.spendline_slider], 
  		style={'padding-top':'10px', 'padding-bottom':'20px',
          		'padding-left':'10px', 'font-size':'1em',
          		'width':'20%'}
        ),
  
  	html.Div(
  		[dcc.Graph(id='spendline')])
		], style={'width':'100%'}
		),

## MAPBOX
html.Div([
		box.dropdown_element,
		dcc.Graph(id='mapbox', figure=box.return_mapbox_scatter())
	], style={'width':'80%','margin':'0 auto', 'height':'auto'}
	),

## GEO GRAPH
html.Div([
    geo.dropdown_element,
    dcc.Graph(id='geoscat', 
	        style={'display':'inline-block','width':'100%',}),],
  	#style={'display':'inline-block','width':'50%'}
    ),

## HEAT MAP
html.Div([
	heat.radio_element,
  	dcc.Graph(id='heatmap',style={'display': 'inline-block', 
  							'width':'100%','height':'100%'}),],
  	#style={'display':'inline-block', 'width':'30%'}
    )

],
style={'width':'80%','border':'1px solid black','margin':'0 auto'},className='main'
)



### CALLBACKS to graph files and fig returners
#GEO
@app.callback(
      Output('geoscat', 'figure'), 
      [Input('state_list', 'value')]
      )
def return_geoscatter_fig(value):
	return geo.return_geoscatter_fig(value)
#LINE
@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value'), Input('line_slider', 'value')]
    )
def line_graph_cb(value, svalue):
    line_graph = lg.ChipotleSpendLine(df, value, svalue)
    return line_graph.ret_graph(value, svalue)
#HEAT
@app.callback(
    Output('heatmap', 'figure'),
    [Input('heat_radio', 'value')])
def ret_heatmap_figure(value):
	return heat.ret_heatmap_figure(value)



if __name__=='__main__':
  print(df.head())
  print(len(df))

  app.run_server(debug=True)

