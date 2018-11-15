import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import flask
from flask_cors import CORS
import os
from collections import OrderedDict
import json
from textwrap import dedent as d

import plotly.graph_objs as go

from sklearn import preprocessing

import pandas.plotting

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app = dash.Dash()

df = pd.read_csv('datajaebsv3.csv')
dff = pd.read_csv('datajaebsv3.csv')
nf = pd.read_csv('gapminderDataFiveYear.csv')

group_label = dff["Group"].values
group_id = dff["ID"].values

dff.reset_index(drop=True, inplace=True)
dff.drop(['ID'], axis=1, inplace=True)
dff.drop(['Group'], axis=1, inplace=True)

pandas.plotting.scatter_matrix(dff)

x = dff.values
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df_normalized = pd.DataFrame(x_scaled, columns = dff.columns)

## PCA
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pca.fit(x_scaled, group_label)
x_transformpca = pca.transform(x_scaled)

app.layout = html.Div([
    # Row 1: Header and Intro text

    html.Div([
        html.Img(src="http://i47.tinypic.com/zs2yr.jpg",
                style={
                    'height': '100px',
                    'float': 'right',
                    'position': 'relative',
                    'bottom': '40px',
                    'left': '50px'
                },
                ),
        html.H2('Gait Analysis',
                style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '10px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '6.0rem',
                    'color': '#4D637F'
                }),
        html.H2('Visualizer',
                style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '27px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '6.0rem',
                    'color': '#4D637F'
                }),
    ], style={'position': 'relative', 'right': '15px'}),


    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='3D PCA', children=[
            html.Div([
            dcc.Graph(
            id='basic-interactions',
                figure={
            'data': [
                {'x': x_transformpca[group_label==1, 0], 'y': x_transformpca[group_label==1, 1],'z':df['Knee_flex_foot_contact'], 'type': 'scatter3d', 'name': 'ASD'},
                {'x': x_transformpca[group_label==2, 0], 'y': x_transformpca[group_label==2, 1],'z':df['Knee_flex_foot_contact'], 'type': 'scatter3d', 'name': 'NOT ASD'},
            ],
            'layout': {
            'automargin':True,
            'scene' :
            {
                'camera' :{

                    'up': {'x':0, 'y':0, 'z':0},
                    'center':{'x':0, 'y':0, 'z':0},
                    'eye':{'x':0.1, 'y':2.5, 'z':0.1}

                }
                

            } 
            }
                }
            )], className='nine columns', style=dict(textAlign='left')),
            html.Div([
            dcc.Markdown(d("""
                **Features**
            """)),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns')

        ]),
        dcc.Tab(label='2D PCA', children=[
                dcc.Graph(
        id='example-graph-2',
        figure={
            'data': [
                {'x': x_transformpca[group_label==1, 0], 'y': x_transformpca[group_label==1, 1], 'type': 'scatter', 'name': 'ASD'},
                {'x': x_transformpca[group_label==2, 0], 'y': x_transformpca[group_label==2, 1], 'type': 'scatter', 'name': 'NOT ASD'},
            ],
            'layout': {
            }
        }
    )
        ]),
        dcc.Tab(label='Add Tab', children=[
                dcc.Graph(id='graph-with-slider'),
            dcc.Slider(
            id='year-slider',
            min=nf['year'].min(),
            max=nf['year'].max(),
            value=nf['year'].min(),
            marks={str(year): str(year) for year in nf['year'].unique()}
            )
        ])
    ])    

], className='container')

@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]


for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server()
