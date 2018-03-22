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

data = Data([dict(type = 'scattergeo',
        locationmode = 'USA-states',
        lon = df_piv['lon'],
        lat = df_piv['lat'],
        text = df_piv['text'],
        marker = dict(
            size = (df_piv['Amount']['sum'])/scale,
            color = 'red',
            line = dict(width=0.5, color='rgb(40,40,40)'),
            sizemode = 'area'
        ),
        )
])

layout = dict(
        title = 'Frequented Chipotles',
        showlegend = False,
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = 'rgb(209, 187, 175)',
            subunitwidth=1,
            countrywidth=1,
            subunitcolor="rgb(255, 255, 255)",
            countrycolor="rgb(255, 255, 255)"
        ),
    )

fig = dict(data=data, layout=layout)


"""@app.callback(
        dash.dependencies.Output('geo_freq', 'figure'),
    [dash.dependencies.Input('state_selector', 'values')])
def filter_graph(values):
    filtered_df = df_piv[df_piv['state'].isin(values)]
    data = dict(
		type = 'scattergeo',
		locationmode = 'USA-states',
		lon = filtered_df['lon'],
		lat = filtered_df['lat'],
		text = filtered_df['text'],
		marker = dict(
		size = (filtered_df['Amount']['sum'])/scale,
		color = 'red',
		line = dict(width=0.5, color='rgb(40,40,40)'),
		sizemode = 'area'),)
    
    return Figure(data=data)"""

if __name__ == '__main__':
    py.plot(fig)



