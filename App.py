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

# 
ch_red = 'rgb(140,21,5)'
ch_brown = 'rgb(69, 20, 0)'
ch_grey = '#686E70'

global_style = {
    'color':ch_grey,
    'font-family': 'verdana',
    'margin-left': '2px',
    'text-align': 'left',
    'width': '80%',
	'left-margin':'5%',
	'right-margin':'5%'
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
df.Date = pd.to_datetime(df['Date'])

### Pivot for geo scatter
df_piv = df.groupby(
                    ['address','store_no','lat','lon', 'state']
                    ).agg({'Amount':['sum','count','mean']}).reset_index()

amounts = df_piv['Amount']
df_piv['short_add'] = df_piv.address.apply(lambda x:re.sub('\w* - .* - ', '',x))
df_piv['text'] = 'Visits: '+amounts['count'].map(str)+\
                  '<br>Avg $: '+amounts['mean'].map(str)+\
                  '<br>Total $: '+amounts['sum'].map(str)+\
                  '<br>'+df_piv['short_add']
scale = .5
###

### Pivot for heatmap
season_str = {1:"Winter", 2:"Spring", 3:"Summer", 4:"Autumn"}
days = {0:'Mon',1:'Tues',2:'Weds',3:'Thurs',4:'Fri',5:'Sat',6:'Sun'}

df_hm = df
df_hm['day_of_week'] = df_hm['Date'].dt.dayofweek
df_hm['day_of_week'] = df_hm['day_of_week'].apply(lambda x: days[x])
df_hm['month'] = df_hm.Date.apply(lambda x: x.month)
df_hm['season'] = df_hm.Date.apply(lambda x:  (x.month%12+3)//3 ).apply(lambda x:
                                                                 season_str[x])
###

dropdown = dcc.Checklist(
    id = 'store-check',
    options = [{'label':k, 'value': k} for k in list(df_piv.state.unique())],
    values = list(df_piv.state.unique())
    )

heatradio = dcc.RadioItems(
    id = 'heat_radio',
    options = [{'label':"Total Spend    ",'value':'sum'}, 
            {'label':'Average Spend   ','value':'mean'}, 
            {'label':'# of Visits','value':'count'}],
    value = 'sum',
    labelStyle={'display':'inline-block'}
    )
###
###
# Create Line Chart
###
scatter_graph = lg.ChipotleSpendLine(df)
scatter_graph = scatter_graph.ret_graph(value='b')
###
###
			
app = dash.Dash()

app.layout  = html.Div([

    html.Div([
      html.H1('chipotl.ME',style=h1_style), 
      html.P("""Analysis of your Chipotle consumption from mint.com transaction
      history""", style=p_style)
    ]),
	
	html.Div([lg.spendline_radio,
	  dcc.Graph(id='spendline')
	], style={'width':'40%'}),

    html.Div([
      dropdown,
      dcc.Graph(id='geoscat', 
            style={'display':'inline-block',
                    'width':'100%',}),
      ],
      style={'display':'inline-block','width':'70%'}
        ),

    html.Div([
      heatradio,
      dcc.Graph(id='heatmap',
            style={'display': 'inline-block', 'width':'100%','height':'100%'}),],
      style={'display':'inline-block', 'width':'30%'}
        )
    ],
  style=global_style,className='zxzxzzx')

@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value')]
    )
def line_graph_cb(value):
    line_graph = lg.ChipotleSpendLine(df, value)
    return line_graph.ret_graph(value)

@app.callback(
    Output('geoscat', 'figure'), 
    [Input('store-check', 'values')]
    )
def filter_geoscat_states(values):
    dff = df_piv[df_piv['state'].isin(values)]
    
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
      title='Location Frequency',
      showlegend=False,
      dragmode="zoom",
      geo=dict(
        center=dict(
            lon=(dff.lon.max()+dff.lon.min())/2,
            lat=(df.lat.max()+df.lat.min())/2,
            showcoastlines=True),
        scope='usa',
        projection=dict(type='albers usa'),
        showland=True,
        landcolor = 'rgb(209, 187, 175)',
        subunitwidth=1,
        countrywidth=1,
        subunitcolor="rgb(255, 255, 255)",
        countrycolor="rgb(255, 255, 255)"
        ),
      height=600,
      jitter=1,
      zoom=10,
      hoverlabel=dict(bgcolor=ch_grey,
                    font=dict(family='verdana', size='9')),
      )
    fig = dict(data=dataf, layout=layoutf)
    return fig

@app.callback(
    Output('heatmap', 'figure'),
    [Input('heat_radio', 'value')])
def ret_heatmap_matrix(value):
    hm = df_hm.pivot_table(index='day_of_week', columns='season', 
                            values='Amount', aggfunc=str(value))
    hm.fillna(0, inplace=True)
    hm = hm[['Spring','Summer','Autumn','Winter']]
    hm = hm.reindex(list(days.values())[::-1])
    trace = Heatmap(z=[hm.values[x] for x in range(0,len(hm.values))],
                   x=hm.columns, y = hm.index, colorscale='YlOrBr')
    layout = dict(title='Common Days', height=600)
    figure = dict(data=[trace], layout=layout)
    return figure

if __name__ == '__main__':
  app.run_server(debug=True)

