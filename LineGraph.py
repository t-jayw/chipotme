import re, sys, dash

import pandas as pd  
import plotly.plotly as py
import dash_html_components as html
import dash_core_components as dcc
import statsmodels.api as sm

from plotly.graph_objs import *

def reverse_order_cum_sum(df, column):
    df['cum_sum'] = df.ix[::-1, column].cumsum()[::-1]
    return df


spendline_radio = dcc.RadioItems(
  id = 'line_radio',
  options = [{'label': 'Over time', 'value':'a'},
             {'label': 'Cumulative Sum', 'value':'b'}],
  value = 'a',
  labelStyle={'display':'inline-block'}
  )

class ChipotleSpendLine(object):
  def __init__(self, df, value='a'):
    self.df = df
    self.df.Date = pd.to_datetime(self.df['Date'])
    self.df = self.prep_data()
    self.value = value
    self.set_trend_col()
    self.set_cs_trend_col()
    self.target = {'a':{'col':'Amount','trend':'trend'},
              'b':{'col':'cum_sum', 'trend':'cs_trend'}}

  def prep_data(self):
    ldf = self.df
    ldf = ldf[['Amount', 'Date']]
    ldf = ldf.set_index('Date')
    ldf['Date'] = ldf.index
    ldf.index = pd.to_datetime(ldf.index)
    ldf['numdate'] = ldf.index.to_julian_date()
    ldf = reverse_order_cum_sum(ldf, 'Amount')
    return ldf

  def set_trend_col(self):
    ldf = self.df
    model = sm.formula.ols(formula='Amount ~ numdate', data=ldf)
    res = model.fit()
    ldf['trend'] = res.fittedvalues
    self.df = ldf
    self.trend = res

  def set_cs_trend_col(self):
    ldf = self.df
    model = sm.formula.ols(formula='cum_sum ~ numdate', data = ldf)
    res = model.fit()
    ldf['cs_trend'] = res.fittedvalues
    self.df = ldf
    self.cs_trend = res
    print(self.df.head())
    
  def make_scatters(self, value):
    spend = Scatter(
      x = self.df['Date'],
      y = self.df[self.target[value]['col']],
      name = 'Spend',
    )
    trend = Scatter(
      x = self.df['Date'],
      y = self.df[self.target[value]['trend']],
      name = 'Trend',
      hoverinfo='none'
    )
    self.data = [spend, trend]
    return [spend, trend]

  def make_lay(self, value='a'):
    col = self.target[value]['trend']
    scatter_lay = Layout(
      yaxis=dict(
        zeroline=True,
        range=[0,max(self.df[col])+5],
        title='Spend in Local Currency'
        ),
        xaxis=dict(title='Date')
    )
    return scatter_lay
  
  def make_fig(self):
    return Figure(data=self.data, layout=self.layout)

  def make_graph(self):
    scatter_graph = dcc.Graph(
      id='spend-line',
      figure=self.fig)
    self.graph = scatter_graph

  def make_graph(self, value='b'):

    data = self.make_scatters(value)
    layout = self.make_lay(value)
    fig = Figure(data=data, layout=layout)
    scatter_graph = dcc.Graph(id='spend-line',
                              figure = fig)
    return fig

  def ret_graph(self,value):
    return self.make_graph(value)
