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
# 

# Load data
data_obj = dm.DataHandler()

df = data_obj.final_df

geo = gs.GeoScatter(df)

app = dash.Dash()

app.layout  = html.Div([

    html.Div([
      html.H1('chipotl.ME'), 
      html.P("""Analysis of your Chipotle consumption from mint.com transaction
      history""")
    ]),
	
	html.Div([
    html.Div([lg.spendline_radio]),
    html.Div(
      [dcc.Markdown('''Forecast Future Values[*](https://xkcd.com/605/)'''),
      lg.spendline_slider], 
      style={'padding-top':'10px', 'padding-bottom':'20px',
              'padding-left':'10px', 'font-size':'1em'}),
	  html.Div([dcc.Graph(id='spendline')])
	], style={'width':'50%'}),

    html.Div([
	  geo.dropdown_element,
	  dcc.Graph(id='geoscat', 
		        style={'display':'inline-block',
		               'width':'100%',}),

		],
      style={'display':'inline-block','width':'50%'}
        ),

    html.Div([
      dcc.Graph(id='heatmap',
            style={'display': 'inline-block', 'width':'100%','height':'100%'}),],
      style={'display':'inline-block', 'width':'30%'}
        )
    ],
  style={},className='zxzxzzx')

@app.callback(
      Output('geoscat', 'figure'), 
      [Input('state_list', 'value')]
      )
def return_geoscatter_fig(value):
	return geo.return_geoscatter_fig(value)

@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value'), Input('line_slider', 'value')]
    )
def line_graph_cb(value, svalue):
    line_graph = lg.ChipotleSpendLine(df, value, svalue)
    return line_graph.ret_graph(value, svalue)

if __name__=='__main__':
  print(df.head())
  print(len(df))

  app.run_server(debug=True)

