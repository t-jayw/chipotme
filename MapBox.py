import re, sys, dash, datetime, math

import pandas as pd  
import plotly.plotly as py
import dash_html_components as html
import dash_core_components as dcc
import statsmodels.api as sm


from plotly.graph_objs import *

from secrets import keys

mapbox_key = keys['mapbox']

class MapBox(object):
	def __init__(self, df):
		self.df = df 
		self.scale = 4000
		self.df_geo = self.create_piv_for_geo()

	def create_piv_for_geo(self):
		df_geo = self.df.groupby(['address', 'store_no', 'lat', 'lon', 'state', 'short_address'])
		df_geo = df_geo.agg({'Amount':['sum', 'count', 'mean']}).reset_index()
		amounts = df_geo['Amount']
		df_geo['text'] = 'Visits: '+amounts['count'].map(str)+\
						'<br>Avg $: '+amounts['mean'].map(str)+\
						'<br>Total $: '+amounts['sum'].map(str)+\
						'<br>'+df_geo['short_address']
		df_geo['size'] = (df_geo['Amount']['sum'].apply(lambda x: x/(1.021**x)))
		return df_geo

	def create_drop_down_element(self):
		dropdown = dcc.Dropdown(
			id = 'state_list',
			options = [{'label':k, 'value': k} for k in list(self.df_geo.state.unique())],
			value = list(self.df_geo.state.unique()),
			multi = True
			)
		return dropdown

	def return_mapbox_scatter(self, value=None):
		dff = self.df_geo

		data = Data([
				Scattermapbox(
					lat=dff['lat'],
					lon=dff['lon'],
					mode='markers',
					marker=Marker(
						size=dff['size'],
						opacity = 0.4
						),
					text=dff['text']
					)
				])

		layout = Layout(
				title="Your favorite spots",
				autosize=True,
				hovermode='closest',
				showlegend=False,
				mapbox=dict(
					accesstoken=mapbox_key,
					bearing=0,
					center=dict(
						lat=38,
						lon=-94
						),
					pitch=0,
					zoom=3,
					style='light'
					),
				)

		fig = dict(data=data, layout=layout)
		return fig
