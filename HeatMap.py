import re, sys, dash, datetime

import pandas as pd  
import plotly.plotly as py
import dash_html_components as html
import dash_core_components as dcc
import statsmodels.api as sm

from plotly.graph_objs import *

class HeatMap():
	def __init__(self, df):
		self.season_str = {1:"Winter", 2:"Spring", 3:"Summer", 4:"Autumn"}
		self.days = {0:'Mon',1:'Tues',2:'Weds',3:'Thurs',4:'Fri',5:'Sat',6:'Sun'}
		self.df = df 
		self.df_hm = self.prep_heatmap_data()
		self.radio_element = self.return_radio_element()


	def prep_heatmap_data(self):
		df_hm = self.df
		
		df_hm['day_of_week'] = df_hm['Date'].dt.dayofweek
		df_hm['day_of_week'] = df_hm['day_of_week'].apply(lambda x: self.days[x])
		df_hm['month'] = df_hm.Date.apply(lambda x: x.month)
		df_hm['season'] = df_hm.Date.apply(lambda x:(x.month%12+3)//3 ).apply(
											lambda x: self.season_str[x])
		return df_hm

	def return_radio_element(self):
		heatradio = dcc.RadioItems(
    		id = 'heat_radio',
    		options = [{'label':"Total Spend    ",'value':'sum'}, 
		            {'label':'Average Spend   ','value':'mean'}, 
		            {'label':'# of Visits','value':'count'}],
    		value = 'sum',
    		labelStyle={'display':'inline-block'}
    		)
		return heatradio

	def ret_heatmap_figure(self, value):
		hm = self.df_hm.pivot_table(index='day_of_week', columns='season',
									values='Amount', aggfunc=str(value))
		hm.fillna(0, inplace=True)
		hm = hm[['Spring', 'Summer', 'Autumn', 'Winter']]
		hm = hm.reindex(list(self.days.values())[::-1])

		trace = Heatmap(z=[hm.values[x] for x in range(0,len(hm.values))],
						x=hm.columns, y=hm.index, colorscale='YlOrBr')
		layout = dict(title='Season/Day Frequency', height=600)
		figure = dict(data=[trace], layout=layout)			

		return figure
