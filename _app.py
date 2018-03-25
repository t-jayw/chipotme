import re, sys, dash, base64, io
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

html.Div([
dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'height': '50px',
        'lineHeight': '50px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
    },
    # Allow multiple files to be uploaded
    multiple=False
), html.P(id="upload", children="please upload")]),

## SPEND LINE
html.Div([
	html.Div(
  		[lg.spendline_radio,
  		dcc.Markdown('''Forecast Future Values[*](https://xkcd.com/605/)'''),
  		lg.spendline_slider], 
  		style={'padding-top':'10px', 'padding-bottom':'20px',
          		'padding-left':'10px', 'font-size':'1em',
          		'width':'100%'}
        ),
  	html.Div(
  		[dcc.Graph(id='spendline')])
		], style={'width':'50%'}
		),

## MAPBOX
html.Div([
		box.dropdown_element, 
		dcc.Graph(id='mapbox',style={'height': '600px', 'width':'100%'}),
	], style={'width':'90%','margin':'0 auto', 'height':'auto'}
	),

## HEAT MAP
html.Div([
	heat.radio_element,
  	dcc.Graph(id='heatmap',style={'display': 'inline-block', 
  							'width':'100%','height':'100%'}),],
  	style={'display':'inline-block', 'width':'50%'}
    ),
html.Div(id="hidden", children="")

], 
style={'width':'70%','border':'1px solid black','margin':'0 auto'},className='main'
)

### CALLBACKS to graph files and fig returners
#GEO
@app.callback(
	Output('upload', 'children'),
	[Input('upload-data', 'contents')]
	)
def do_something(contents):
	if contents is None:
		ret = "AHDFHSD"
	else:
		content_type, content_string = contents.split(',')
		decoded = base64.b64decode(content_string)
		df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
		ret = df.head().to_json()
		print(df.head())
		run_it()


	return_geoscatter_fig(['CO'])

	return ret


@app.callback(
      Output('mapbox', 'figure'), 
      [Input('map_state_list', 'value')]
      )
def return_geoscatter_fig(value):
	print(value)
	return box.return_mapbox_scatter(value)

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

  app.run_server(debug=True)

