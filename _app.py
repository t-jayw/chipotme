import re, sys, dash, base64, io
import pandas as pd
import requests as r
import zipcodes as zc
import matplotlib.pyplot as plt
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import statsmodels.api as sm
import stylefile as s


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
ch_red = 'rgb(140,21,5)'
ch_brown = 'rgb(69, 20, 0)'
ch_grey = '#686E70'
background = '#F2EEE4'

h1_style= {
    'color': ch_red,
    'width': '100%',
    'font-size': '3em',
    'margin-top': '20px',
    'margin-bottom': '20px',
    'font-weight': 'bolder',
    'text-align': 'center'}
h4_style= {
    'color': ch_red,
    'width': '100%',
    'font-size': '1.2em',
    'margin-top': '20px',
    'margin-bottom': '10px',
    'font-weight': 'bolder'}
p_style = {
	'color': ch_grey,
	'font-size': '.9em',
	'margin-top': '2px',
	'margin-bottom': '2px',
	'text-align': 'center'
}
global_style = {
    'color':ch_grey,
    'font-family': 'verdana',
    'margin-left': '2px',
    'text-align': 'center',
    'width': '90%',
	  'left-margin':'5%',
	  'right-margin':'5%',
    'height':'100%',
    'background-color':background,
    'margin':'0 auto'
    }
# Load data

data_obj = dm.DataHandler()

df = data_obj.final_df

geo = gs.GeoScatter(df)
heat = hm.HeatMap(df)

app = dash.Dash()

map_drop_down_options = 'CO'

app.layout  = html.Div([

html.Div([
	html.H1('chipot.me', style=h1_style), 
	html.P("""Analysis of Chipotle consumption from mint.com transaction history""",
				style = p_style)
]),

html.Div([
	dcc.Upload(
	    id='upload-data',
	    children=html.Div([
	        '',
	        html.A('Click to Upload File')
	    ]),
	    style={
	        'width': '20%',
	        'height': '40px',
	        'lineHeight': '40px',
	        'borderWidth': '1px',
	        'borderStyle': 'dashed',
	        'borderRadius': '5px',
	        'textAlign': 'center',
	    },
	    # Allow multiple files to be uploaded
	    multiple=False
	), 
	html.P(id="data_source", children="Using stock data.", style={'text-align':'left'})]
	),

## SPEND LINE
html.Div([

	html.Div([
		html.Div([
			html.H4('Spending over time', style=h4_style),
			html.P('''Select the `Cumulative Sum` option for a running total''', style=p_style),
			html.H4('''Forecast Slider''', style=h4_style),
			html.P('''A univariate logistic regression fit to the transaction data predicts future values''', style=p_style),
		], 		
		style={'width':'100%', 'display':'inline-block',
		'borderBottomWidth':'8px','borderBottomStyle': 'solid', 'border-bottom-color':ch_grey}
		),
		html.Div(
	  		[lg.spendline_radio,
	  		dcc.Markdown('''Forecast Future Values[*](https://xkcd.com/605/)'''),
	  		lg.spendline_slider], 
	  		style={'padding-top':'10px', 'padding-bottom':'20px',
	          		'padding-left':'20px', 'font-size':'.8em',
	          		'width':'50%', 'text-align':'left'}
	        ),
	  	html.Div(
	  		[dcc.Graph(id='spendline')])
		], 
		style={'width':'90%','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
		),
		],

	),

## MAPBOX
html.Div([
	html.Div([
		html.H4('Commonly visited locations', style=h4_style),
		html.P('''Each dot is a Chipotle location where there is a transaction.''', style=p_style),
		html.P("""The dots are scaled by total spend at a given location.""", style=p_style),
		html.P("""If there are multiple states, you can select and deselect them with the dropdown.""", style=p_style),
		html.P("""Making the graph automatically resize took me forever, so please enjoy it""", style=p_style),
		], style={'borderBottomWidth':'8px','borderBottomStyle': 'solid', 'border-bottom-color':ch_grey, }
	),
	dcc.Dropdown(
		id = 'map_state_list',
		multi = True
		),
	dcc.Graph(id='mapbox',style={'height': '550px', 'width':'100%', 'margin-top':'20px'}),
	], 
	style={'width':'90%','margin':'0 auto', 'height':'auto','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
	),

## HEAT MAP


html.Div([
	html.H4('Heatmap for seasonal visitation trends', style=h4_style),
	html.P('Select aggregations by Total spend, Average spend, or count of visits', style=p_style),
	dcc.RadioItems(
		id = 'heat_radio',
		options = [{'label':"Total Spend    ",'value':'sum'}, 
		        {'label':'Average Spend   ','value':'mean'}, 
		        {'label':'# of Visits','value':'count'}],
		value = 'sum',
		labelStyle={'display':'inline-block'}),
  	dcc.Graph(id='heatmap',style={ 
  							'width':'50%','height':'100%', 'margin':'0 auto',}),
  	],
  	style={'width':'90%', 'margin':'0 auto','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
    ),


html.Div(id="json_store", children="", style={'display': 'none'})
], 
style=global_style,
className='main'
)




######################################################################
### CALLBACKS to graph files and fig returners
########## INPUT
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
	Output('data_source', 'children'),
	[Input('json_store', 'children')]
	)
def switch_data_source(children):
	if children != '':
		return 'Showing user uploaded data'
	else:
		return 'Showing stock data'

############### GEO 
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


############## LINE
@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value'), Input('line_slider', 'value'), Input('json_store', 'children')]
    )
def line_graph_cb(value, svalue, children):
	ldf = df if children == '' else pd.read_json(children)
	line_graph = lg.ChipotleSpendLine(ldf, value, svalue, children)
	return line_graph.ret_graph(value, svalue)
		


################## HEAT
@app.callback(
    Output('heatmap', 'figure'),
    [Input('heat_radio', 'value'), Input('json_store', 'children')])
def ret_heatmap_figure(value, children):
	print('I AM HEAT CALL')
	hdf = df if children == '' else pd.read_json(children)
	heat = hm.HeatMap(hdf)
	return heat.ret_heatmap_figure(value)




if __name__=='__main__':

  map_drop_down_options = []

  app.run_server(debug=True)

