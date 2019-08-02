import dash
from dash.dependencies import Input,Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Weather Observation Points UK'

df = pd.read_csv('location_detail_final_v3.csv')

#generate the region textboxes from the data
#much easier to maintain than manually doing it
def regionCheckBoxes():
    region_list = df['region'].unique().tolist()
    dicts_list = []
    for region in region_list:
        dicts_list.append({'label':region,'value':region})

    return dcc.Dropdown(id='region-check-boxes',
        options=dicts_list,
        value=[],
        multi=True)

app.layout = html.Div(children=[

    html.Div([
        html.Div([html.H4('Uk Weather Observation Stations')]),
        html.Div([regionCheckBoxes()]) 
    ]),

    html.P('Slide to change Elevation'),
    html.Tr([
    html.Td([dcc.Slider(id='elevation-slider',
    min=df['elevation'].min(),
    max=df['elevation'].max(),
    step=10,
    value=(df['elevation'].max()/2)),dcc.Graph(id='stations-graph')]),
    html.Td([dcc.Graph(id='regions-bar-graph')]),
        ])
    ])

#methods for callbacks and callbacks
def buildGraph(lat_df,lon_df,name_df,elevation_df):
    new_figure = go.Figure(data=go.Scattergeo(
    lat = lat_df,
    lon = lon_df,
    text = name_df,
    marker = dict(
        color = elevation_df,
        colorscale = 'thermal',
        reversescale = True,
        opacity = 0.7,
        size = 3,
        colorbar = dict(
            titleside = "top",
            outlinecolor = "rgba(68, 68, 68, 0)",
            ticks = "outside",
            title='Elevation',
            showticksuffix = "last",
            dtick = 100))
    ))

    new_figure.update_layout(
    geo = dict(
        domain = dict(x=[0,1],y=[0,1]),
        scope = 'europe',
        showland = True,
        landcolor = "rgb(212, 212, 212)",
        subunitcolor = "rgb(255, 255, 255)",
        countrycolor = "rgb(255, 255, 255)",
        showlakes = True,
        lakecolor = "rgb(255, 255, 255)",
        showsubunits = True,
        showcountries = True,
        resolution = 50,
        uirevision='stations-graph',
        projection = dict(type = 'robinson'),
        center= dict(lon=-5,lat=55)
    ))
    #title='Uk Weather Observation Stations: ')
    return new_figure

#start callbacks
@app.callback(Output(component_id='regions-bar-graph',component_property='figure'),
[Input('region-check-boxes','value')])
def makeBarGraph(input_choice):
    #regional_df = df[df['region'].isin(input_choice)]
    count_stations = df['region'].value_counts()
    df_bind = pd.DataFrame(columns=['region','count'])
    df_bind['region'] = df['region'].unique()
    df_bind['count'] = count_stations.values

    y_vals = df_bind[df_bind['region'].isin(input_choice)]['count']
    print(y_vals)

    #problem occurs because the x axis value is deleted
    #but the y value persists
    #additionally, the graph sorts highest to smalelst
    #but it isn't also moving the labels
    graph_fig = go.Figure(
    data=[go.Bar(x=input_choice, y=y_vals)],
    layout=go.Layout(
        xaxis=dict(type='category'),
        width=500,
        height=500,
        title=go.layout.Title(text="Number of Stations in Region"))
    )

    return graph_fig

@app.callback(Output(component_id='stations-graph',component_property='figure'),
[Input('region-check-boxes','value'),Input('elevation-slider','value')])
def remodelGraph(input_choice,input_value):

    #must have region selected before elevation is considered
    regional_df = df[df['region'].isin(input_choice)]

    master_ele_df = regional_df[regional_df['elevation'] <= input_value]
    lat_df = master_ele_df['latitude']
    lon_df = master_ele_df['longitude']
    name_df = master_ele_df['name']
    elevation_df = master_ele_df['elevation']

    return buildGraph(lat_df,lon_df,name_df,elevation_df)

if __name__ == '__main__':
    app.run_server(debug=True)
