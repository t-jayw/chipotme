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
		self.df_geo = self.create_piv_for_geo()
		self.scale = 4000

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

	def return_drop_down_list(self):
		return [{'label':k, 'value': k} for k in list(self.df_geo.state.unique())]


	def test_zoom(self, lat, lon):

		sq = (lat * lon)
		lsq = math.log(sq+.01)
		x = math.log(lat * lon+.01)
		b = 7.3
		m = -0.7283

		zoom = (m*x)+b

		if sq == 0:
			zoom = 12

		if lon >= 40:
			zoom = 2.7


		p = '[%s,%s,%s]'%(lat, lon, zoom)
		return(zoom)


	def return_mapbox_scatter(self, value):
		if value == []:
			value = list(self.df_geo.state.unique())
		dff = self.df_geo[self.df_geo['state'].isin(value)]

		lon_range = (dff.lon.max()-dff.lon.min())
		lat_range = dff.lat.max()-dff.lat.min()

		data = Data([
				Scattermapbox(
					lat=dff['lat'],
					lon=dff['lon'],
					mode='markers',
					marker=Marker(
						size=dff['size'],
						opacity = 0.4,
						color = 'rgb(140,21,5)'
						),
					text=dff['text']
					)
				])

		layout = Layout(
				title="Visited Chipotle Stores",
				autosize=True,
				hovermode='closest',
				showlegend=False,
				margin=dict(l=80,r=80,t=80,b=80),
				paper_bgcolor='#FBF9F6',
				mapbox=dict(
					accesstoken=mapbox_key,
					bearing=0,
					center=dict(
						lon=(dff.lon.max()+dff.lon.min())/2,
              			lat=(dff.lat.max()+dff.lat.min())/2
						),
					pitch=0,
					zoom=self.test_zoom(lat_range, lon_range),
					#zoom=self.ret_zoom_level(lat_range, lon_range),
					style='light'
					),
				)
		print(layout.mapbox.zoom)
		type(self).layout_zoom = layout.mapbox.zoom
		fig = dict(data=data, layout=layout)
		return fig


