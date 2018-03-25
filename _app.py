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

app = dash.Dash()

map_drop_down_options = 'CO'

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

html.Button(id='propagate-button', n_clicks=0, children='Propagate Table Data'),

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
		dcc.Dropdown(
			id = 'map_state_list',
			multi = True
			),
		dcc.Graph(id='mapbox',style={'height': '600px', 'width':'100%'}),
	], style={'width':'90%','margin':'0 auto', 'height':'auto'}
	),

## HEAT MAP
html.Div([
	dcc.RadioItems(
		id = 'heat_radio',
		options = [{'label':"Total Spend    ",'value':'sum'}, 
		        {'label':'Average Spend   ','value':'mean'}, 
		        {'label':'# of Visits','value':'count'}],
		value = 'sum',
		labelStyle={'display':'inline-block'}),
  	dcc.Graph(id='heatmap',style={'display': 'inline-block', 
  							'width':'100%','height':'100%'}),],
  	style={'display':'inline-block', 'width':'50%'}
    ),
html.Div(id="json_store", children="")

], 
style={'width':'70%','border':'1px solid black','margin':'0 auto'},className='main'
)

### CALLBACKS to graph files and fig returners
#GEO
@app.callback(
	Output('json_store', 'children'),
	[Input('upload-data', 'contents')]
	)
def do_something(contents): ### TO DO <-- make this a real class with nice functions
	if contents is None:
		ret = ""
	else:
		content_type, content_string = contents.split(',')
		decoded = base64.b64decode(content_string)
		df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
		new_DataObj = dm.DataHandler(df)
		print('have new data')

		ret = new_DataObj.final_df.to_json()
	### if it found a valid CSV, spit out a json blob of it for other classes to handle
	return ret

@app.callback(
		Output('map_state_list', 'value'),
		[Input('json_store', 'children')]
	)
def return_geoscatter_dropdownvals(children):
	mbdf = df if children == '' else pd.read_json(children)
	box = mb.MapBox(mbdf)
	return mbdf.state.unique()

@app.callback(
      Output('mapbox', 'figure'), 
      [Input('map_state_list', 'value'), Input('json_store', 'children')]
      )
def return_geoscatter_fig(value, children):
	mbdf = df if children == '' else pd.read_json(children)
	box = mb.MapBox(mbdf)
	return box.return_mapbox_scatter(value)

@app.callback(
      Output('map_state_list', 'options'), 
      [Input('json_store', 'children')]
      )
def return_geoscatter_dropdownopts(children):
	print(children)
	mbdf = df if children == '' else pd.read_json(children)
	mbox = mb.MapBox(mbdf)
	print('HIIII')
	print(mbox.return_drop_down_list())
	return mbox.return_drop_down_list()







#LINE
@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value'), Input('line_slider', 'value'), Input('json_store', 'children')]
    )
def line_graph_cb(value, svalue, children):
	ldf = df if children == '' else pd.read_json(children)
	line_graph = lg.ChipotleSpendLine(ldf, value, svalue, children)
	return line_graph.ret_graph(value, svalue)
		




#HEAT
@app.callback(
    Output('heatmap', 'figure'),
    [Input('heat_radio', 'value'), Input('json_store', 'children')])
def ret_heatmap_figure(value, children):
	hdf = df if children == '' else pd.read_json(children)
	heat = hm.HeatMap(hdf)
	return heat.ret_heatmap_figure(value)




if __name__=='__main__':

  map_drop_down_options = []

  app.run_server(debug=True)

