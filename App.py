import dash, base64, io

import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py

from plotly.graph_objs import *
from dash.dependencies import Input, Output

from chipotme import LineGraph as lg
from chipotme import new_DataModel as dm
from chipotme import HeatMap as hm
from chipotme import MapBox as mb
from chipotme import Summary as s
#
ch_red = 'rgb(140,21,5)'
ch_brown = 'rgb(69, 20, 0)'
ch_grey = '#686E70'
background = '#F2EEE4'

h1_style= {
    'color': ch_red,
    'width': '100%',
    'font-size': '3em',
    'margin-top': '20px',
    'margin-bottom': '20px',
    'font-weight': 'bolder',
    'text-align': 'center'}
h4_style= {
    'color': ch_red,
    'width': '100%',
    'font-size': '1.2em',
    'margin-top': '20px',
    'margin-bottom': '10px',
    'font-weight': 'bolder'}
p_style = {
	'color': ch_grey,
	'font-size': '.9em',
	'margin-top': '2px',
	'margin-bottom': '2px',
	'text-align': 'center'
}
global_style = {
    'color':ch_grey,
    'font-family': 'verdana',
    'margin-left': '2px',
    'text-align': 'center',
    'width': '90%',
	  'left-margin':'5%',
	  'right-margin':'5%',
    'height':'100%',
    'background-color':background,
    'margin':'0 auto'
    }



# Load data

data_obj = dm.DataHandler()

df = data_obj.final_df
heat = hm.HeatMap(df)

app = dash.Dash()


app.layout  = html.Div([

html.Div([
	html.H1('chipot.me', style=h1_style),
	html.P("""Analysis of Chipotle consumption from mint.com transaction history""",
				style = p_style),
	html.P("""By default this app will use a default dataset to render the graphs.
				If you'd like to update the app with your own Chipotle transactions click below.""",
				style = p_style),
	html.Button("""Upload your own data""",id='show_upload', style=p_style),
	html.Div([
		html.H4('''How to upload your own data''', style=h4_style),
		html.P('''This app specifically uses Mint.com transaction data.''', style=p_style),
		html.H4('''Follow these instructions to export your Chipotle transactions to a CSV file''', style = p_style),
		html.P('''1. Sign into Mint and go to the 'Transactions' tab''',style=p_style),
		html.P('''2. In the search bar enter 'Chipotle' and hit enter''', style=p_style),
		html.P('''3. Scroll through and confirm that these are all Chipotle transactions''', style=p_style),
		html.P('''4. At the bottom of the screen find 'Export all ... transacations' and click that''', style=p_style),
		html.P('''5. This will start a download of a file called 'transactions.csv', this exact
					 file is the one that you will upload via the selector below.''', style=p_style),
		html.A(href='https://imgur.com/a/zLTBE', children='Click here to see images of the steps',
				target='_blank'),
		html.P('''Please note that if you follow the steps above you will only be sending Chipotle transactions,
					and no personal information.''', style=p_style),
		html.P('''Of what you send, I will filter to just Chipotle anyways, and MAY retain data such as
				 which store locations are popular among users of the app, and transaction data for population statistics''', style=p_style),
		html.H4('''I don't want any thing except Chipotle transactions, so don't send it!!!''', style=p_style),
		html.Br(),
		html.H4('''Please check the box below BEFORE uploading your data if it's okay for me
					to log your anonymized chipotle transactions!''', style=p_style),
		html.P('''If it's unselected the app will still run, no transaction data will be stored''', style=p_style),

		html.Br(),
		html.Div([
			dcc.Upload(
			    id='upload-data',
			    children=html.Div([
			        '',
			        html.A('Upload Data', style={'color':ch_red, 'font-weight':'bolder'}),
			    ],),
			    style={
			        'width': '20%',
			        'height': '40px',
			        'lineHeight': '40px',
			        'borderWidth': '3px',
			        'borderStyle': 'solid',
			        'borderRadius': '5px',
			        'textAlign': 'center',
			        'background-color':'#9E9D72',
			        'display':'inline-block'
			    },
			    # Allow multiple files to be uploaded
			    multiple=False
				),
			dcc.Checklist(id='rec_data',
				options=[
				{'label':'You can save my anonymous Chipotle transaction info','value':1},
				], values=[], style={'display':'inline-block'})
			]),
		], id='upload-info',
			style={}),
	html.H4(id="data_source", children="Showing Data from All Users", style={
		**p_style,**{'borderBottomStyle':'solid'},
					'borderBottomWidth': '8px',
					'padding-bottom':'10px',
					'borderBottomColor':ch_red}),
	html.A(href='https://github.com/t-jayw/chipotme', children='source code', style={'font-size':'10px'}),

]),

## SPEND LINE
html.Div([
	html.Div(
		[dcc.Markdown(id='summary-markdown')
		], style={'text-align':'left', 'padding-left':'5%', }),
	], style={'width':'90%',}),

## SPEND LINE
html.Div([

	html.Div([
		html.Div([
			html.H4('Spending over time', style=h4_style),
			html.P('''Select the `Cumulative Sum` option for a running total''', style=p_style),
			html.H4('''Forecast Slider''', style=h4_style),
			html.P('''A univariate linear regression fit to the transaction data predicts future values''', style=p_style),
		],
		style={'width':'100%', 'display':'inline-block',
		'borderBottomWidth':'8px','borderBottomStyle': 'solid', 'border-bottom-color':ch_grey}
		),
		html.Div(
	  		[lg.spendline_radio,
	  		dcc.Markdown('''Forecast Future Values[*](https://xkcd.com/605/)'''),
	  		lg.spendline_slider],
	  		style={'padding-top':'10px', 'padding-bottom':'20px',
	          		'padding-left':'20px', 'font-size':'.8em',
	          		'width':'50%', 'text-align':'left'}
	        ),
	  	html.Div(
	  		[dcc.Graph(id='spendline')])
		],
		style={'width':'90%','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
		),
		],

	),

## MAPBOX
html.Div([
	html.Div([
		html.H4('Commonly visited locations', style=h4_style),
		html.P('''Each dot is a Chipotle location where there is a transaction.''', style=p_style),
		html.P("""The dots are scaled by total spend at a given location.""", style=p_style),
		html.P("""If there are multiple states, you can select and deselect them with the dropdown.""", style=p_style),
		html.P("""Making the graph automatically resize took me forever, so please enjoy it""", style=p_style),
		], style={'borderBottomWidth':'8px','borderBottomStyle': 'solid', 'border-bottom-color':ch_grey, }
	),
	dcc.Dropdown(
		id = 'map_state_list',
		multi = True
		),
	dcc.Graph(id='mapbox',style={'height': '550px', 'width':'100%', 'margin-top':'20px'}),
	],
	style={'width':'90%','margin':'0 auto', 'height':'auto','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
	),

## HEAT MAP


html.Div([
	html.H4('Heatmap for seasonal visitation trends', style=h4_style),
	html.P('Select aggregations by Total spend, Average spend, or count of visits', style=p_style),
	dcc.RadioItems(
		id = 'heat_radio',
		options = [{'label':"Total Spend    ",'value':'sum'},
		        {'label':'Average Spend   ','value':'mean'},
		        {'label':'# of Visits','value':'count'}],
		value = 'sum',
		labelStyle={'display':'inline-block'}),
  	dcc.Graph(id='heatmap',style={
  							'width':'50%','height':'100%', 'margin':'0 auto',}),
  	],
  	style={'width':'90%', 'margin':'0 auto','borderWidth':'2px',
		'borderStyle': 'solid', 'borderColor': ch_brown, 'margin':'0 auto'}
    ),


html.Div(id="json_store", children="", style={'display': 'none'})
],
style=global_style,
className='main'
)




######################################################################

### SHOW UPLOAD DIV
@app.callback(
	Output('upload-info', 'style'),
	[Input('show_upload', 'n_clicks')]
	)
def show_upload_info(n_clicks):
	if not n_clicks or n_clicks%2 == 0:
		return {'visibility':'hidden', 'height':'0px'}
	else:
		return {}

### CALLBACKS to graph files and fig returners
########## INPUT
@app.callback(
	Output('json_store', 'children'),
	[Input('upload-data', 'contents'),
	Input('rec_data', 'values')]
	)
def do_something(contents, rec_data): ### TO DO <-- make this a real class with nice functions
	if contents is None:
		ret = ""
	else:
		content_type, content_string = contents.split(',')
		decoded = base64.b64decode(content_string)
		df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
		new_DataObj = dm.DataHandler(df, rec_data)

		ret = new_DataObj.final_df.to_json()
	### if it found a valid CSV, spit out a json blob of it for other classes to handle
	return ret

@app.callback(
	Output('data_source', 'children'),
	[Input('json_store', 'children')]
	)
def switch_data_source(children):
	if children != '':
		return 'Showing user uploaded data'
	else:
		return 'Showing all saved transaction data'

####### SUMMARY
@app.callback(
	Output('summary-markdown', 'children'),
	[Input('json_store', 'children')]
	)
def create_summary(children):
	sdf = df if children == '' else pd.read_json(children)
	summ = s.Summary(sdf)
	md = summ.markdown()
	return(md)

############### GEO
@app.callback(
		Output('map_state_list', 'value'),
		[Input('json_store', 'children')]
	)
def return_geoscatter_dropdownvals(children):
	mbdf = df if children == '' else pd.read_json(children)
	box = mb.MapBox(mbdf)
	return mbdf.state.unique()

@app.callback(
      Output('mapbox', 'figure'),
      [Input('map_state_list', 'value'), Input('json_store', 'children')]
      )
def return_geoscatter_fig(value, children):
	mbdf = df if children == '' else pd.read_json(children)
	box = mb.MapBox(mbdf)
	return box.return_mapbox_scatter(value)

@app.callback(
      Output('map_state_list', 'options'),
      [Input('json_store', 'children')]
      )
def return_geoscatter_dropdownopts(children):
	mbdf = df if children == '' else pd.read_json(children)
	mbox = mb.MapBox(mbdf)
	return mbox.return_drop_down_list()

############## LINE
@app.callback(
    Output('spendline', 'figure'),
    [Input('line_radio', 'value'), Input('line_slider', 'value'), Input('json_store', 'children')]
    )
def line_graph_cb(value, svalue, children):
	ldf = df if children == '' else pd.read_json(children)
	line_graph = lg.ChipotleSpendLine(ldf, value, svalue, children)
	return line_graph.ret_graph(value, svalue)

################## HEAT
@app.callback(
    Output('heatmap', 'figure'),
    [Input('heat_radio', 'value'), Input('json_store', 'children')])
def ret_heatmap_figure(value, children):
	hdf = df if children == '' else pd.read_json(children)
	heat = hm.HeatMap(hdf)
	return heat.ret_heatmap_figure(value)


if __name__=='__main__':
  app.run_server(debug=True)

