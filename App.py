import re, sys, dash
import pandas as pd
import requests as r
import zipcodes as zc
import matplotlib.pyplot as plt
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py

from plotly.graph_objs import *
from bs4 import BeautifulSoup as bs
from dash.dependencies import Input, Output
from textwrap import dedent as d

# 
ch_red = 'rgb(140,21,5)'
ch_brown = 'rgb(69, 20, 0)'
ch_grey = '#686E70'

global_style = {
    'color':ch_grey,
    'font-family': 'verdana',
    'margin-left': '7px',
    'text-align': 'left',
    }
h1_style= {
    'color': ch_red,
    'width': '100%',
    'font-size': '3em',
    'margin-top': '20px',
    'margin-bottom': '20px',
    'font-weight': 'bolder'}
p_style = {}



# Load data
df = pd.read_csv('data/chipotle_df.csv')

df_piv = df.groupby(
                    ['address','store_no','lat','lon', 'state']
                    ).agg({'Amount':['sum','count','mean']}).reset_index()

amounts = df_piv['Amount']
df_piv['text'] = 'Visits: '+amounts['count'].map(str)+\
                  '<br>Avg $: '+amounts['mean'].map(str)+\
                  '<br>Total $: '+amounts['sum'].map(str)+\
                  '<br>'+df_piv['address']
scale = .5

dropdown = dcc.Checklist(
    id = 'store-check',
    options = [{'label':k, 'value': k} for k in list(df_piv.store_no.unique())],
    values = list(df_piv.store_no.unique())
    )

app = dash.Dash()

app.layout  = html.Div([
    html.Div([
      html.H1('chipotl.ME',style=h1_style), 
      html.P("""Analysis of your Chipotle consumption from mint.com transaction
      history""", style=p_style)
    ]),

    html.Div([dropdown
    ]),

    html.Div([
    dcc.Graph(id='geoscat')
    ]),

  ],
  style=global_style)


@app.callback(
    Output('geoscat', 'figure'), 
    [Input('store-check', 'values')]
    )
def filter_geoscat_states(values):
    dff = df_piv[df_piv['store_no'].isin(values)]
    
    dataf = [dict(
    type='scattergeo',
    locationmode='USA-states',
    lon=dff['lon'],
    lat=dff['lat'],
    text=dff['text'],
    marker=dict(
      size=(dff['Amount']['sum'])/scale,
      color=ch_red,
      opacity=0.4,
      line=dict(width=0.5, color='rgb(40,40,40)'),
      sizemode='area')
    )]

    layoutf = dict(
      title='TEst',
      showlegend=False,
      dragmode="zoom",
      geo=dict(
        scope='usa',
        projection=dict(type='albers usa'),
        showland=True,
        landcolor = 'rgb(209, 187, 175)',
        subunitwidth=1,
        countrywidth=1,
        subunitcolor="rgb(255, 255, 255)",
        countrycolor="rgb(255, 255, 255)"
        ),
      height=700,
      jitter=1
      )
    fig = dict(data=dataf, layout=layoutf)
    return fig

if __name__ == '__main__':
  app.run_server(debug=True)

