import re, sys, dash, datetime

import pandas as pd  
import plotly.plotly as py
import dash_html_components as html
import dash_core_components as dcc
import statsmodels.api as sm

from plotly.graph_objs import *

class GeoScatter():
  def __init__(self, df):
    self.df = df 
    self.df_geo = self.create_piv_for_geo()
    self.dropdown_element = self.create_drop_down_element()
    self.scale = 0.5


  def create_piv_for_geo(self):
    df_geo = self.df.groupby(['address', 'store_no', 'lat', 'lon', 'state', 'short_address'])
    df_geo = df_geo.agg({'Amount':['sum', 'count', 'mean']}).reset_index()
    amounts = df_geo['Amount']
    df_geo['text'] = 'Visits: '+amounts['count'].map(str)+\
                    '<br>Avg $: '+amounts['mean'].map(str)+\
                    '<br>Total $: '+amounts['sum'].map(str)+\
                    '<br>'+df_geo['short_address']

    return df_geo

  def create_drop_down_element(self):
    dropdown = dcc.Dropdown(
      id = 'state_list',
      options = [{'label':k, 'value': k} for k in list(self.df_geo.state.unique())],
      value = list(self.df_geo.state.unique()),
      multi = True
      )
    return dropdown

  
  def return_geoscatter_fig(self, value):
      dff = self.df_geo[self.df_geo['state'].isin(value)]

      print(dff.head())
      
      dataf = [dict(
        type='scattergeo',
        locationmode='USA-states',
        lon=dff['lon'],
        lat=dff['lat'],
        text=dff['text'],
        marker=dict(
          size=(dff['Amount']['sum'])/self.scale,
          #color=ch_red,
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
              lat=(dff.lat.max()+dff.lat.min())/2,
              showcoastlines=True),
          scope='usa',
          projection=dict(type='albers usa'),
          showland=True,
          showlakes=True,
          landcolor = 'rgb(209, 187, 175)',
          subunitwidth=1,
          countrywidth=1,
          subunitcolor="rgb(255, 255, 255)",
          countrycolor="rgb(255, 255, 255)"
          ),
        height=600,
        jitter=1,
        zoom=10,
        #plot_bgcolor=background,
        hoverlabel=dict(
                      font=dict(family='verdana', size='9')),
        )
      fig = dict(data=dataf, layout=layoutf)
      return fig