import re, sys, dash, datetime

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

spendline_slider = dcc.Slider(
  id = 'line_slider',
  min = 0,
  max = 5,
  step=None,
  marks={
    0: 'Now',
    1: '1 yr',
    2: '2 yrs',
    3: '3 yrs',
    4: '4 yrs',
    5: '5 yrs'},
  value = 0,
  updatemode='drag'

)

class ChipotleSpendLine(object):
  def __init__(self, df, value='a', slide_value='0', children=''):
    self.df = df
    self.target = {'a':{'col':'Amount','trend':'trend'},
              'b':{'col':'cum_sum', 'trend':'cs_trend'}}
    self.df.Date = pd.to_datetime(self.df['Date'])
    self.df = df.sort_values(by='Date')
    self.base = df.Date.max()
    self.df = self.prep_data()
    self.set_trend_col()
    self.set_cs_trend_col()
    self.forecast()
    self.trim_df(slide_value)
    self.value = value
    print(self.df[:10])

  def prep_data(self):
    ldf = self.df
    ldf = ldf[['Amount', 'Date']]
    ldf = ldf.set_index('Date')
    ldf['Date'] = ldf.index
    ldf.index = pd.to_datetime(ldf.index)
    ldf['numdate'] = ldf.index.to_julian_date()
    ldf['cum_sum'] = ldf.Amount.cumsum()
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
    
  def forecast(self, max_years = 5):
    numdays = 365 * max_years
    base = self.base
    date_list = [base + datetime.timedelta(days=x) for x in range(0, numdays)]
    extension = pd.DataFrame(index=date_list)
    extension['numdate'] = extension.index.to_julian_date()
    extension['Date'] = extension.index
    extension[self.target['a']['col']] = None
    extension[self.target['b']['col']] = None
    extension = extension.assign(trend = lambda x: self.trend.predict(x))
    extension = extension.assign(cs_trend = lambda x: self.cs_trend.predict(x))
    ex_df = self.df.append(extension)
    self.df = ex_df

  def trim_df(self, slide_value):
    max_date = self.base + datetime.timedelta(days = 365*int(slide_value))
    self.plot_df = self.df[self.df.index <= max_date]

  def make_scatters(self, value):
    spend = Scatter(
      x = self.plot_df['Date'],
      y = self.plot_df[self.target[value]['col']],
      name = 'Spend',
      line = dict(color = 'rgb(140,21,5)' )
    )
    trend = Scatter(
      x = self.plot_df['Date'],
      y = self.plot_df[self.target[value]['trend']],
      name = 'Trend', 
      line = dict(color = 'rgb(69, 20, 0)')
    )
    self.data = [spend, trend]
    return [spend, trend]

  def make_lay(self, value='a'):
    title_options = {'a':'Purchases over Time','b':'Cumulative Purchases'}
    col = self.target[value]['trend']
    scatter_lay = Layout(
      title = title_options[value],
      yaxis=dict(
        zeroline=True,
        range=[0,max(self.plot_df[col])+8],
        title='Spend in Local Currency'
        ),
        xaxis=dict(title='Date'),
    height=400,
    paper_bgcolor='#FBF9F6'
    )
    print('range: '+str(scatter_lay.yaxis.range))
    print(max(self.plot_df[col]))
    return scatter_lay
  
  def make_graph(self):
    scatter_graph = dcc.Graph(
      id='spend-line',
      figure=self.fig)
    self.graph = scatter_graph

  def make_graph(self, value='b', svalue='0'):
    self.trim_df(svalue)
    data = self.make_scatters(value)
    layout = self.make_lay(value)
    fig = Figure(data=data, layout=layout)
    scatter_graph = dcc.Graph(id='spend-line',
                              figure = fig)
    return fig

  def ret_graph(self,value, svalue):
    return self.make_graph(value, svalue)
