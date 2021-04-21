import os
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json
import numpy as np
import datetime
import plotly.graph_objects as go
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Sentiment Towards Lockdown in the UK'

# Read data
df_covid_stats = pd.read_csv('data/COVID-Dataset/uk_covid_stats.csv')
uk_counties = json.load(open('data/Geojson/uk_counties_simpler.json', 'r'))
geo_df = pd.read_csv('data/year_data.csv')

# Initial map
date = '2020-03-20'
geo_df = geo_df.loc[geo_df['date'] == date]
fig_0 = px.choropleth_mapbox(
    geo_df, 
    locations="id", 
    featureidkey='properties.id', 
    geojson=uk_counties,
    color='sentiment', 
    hover_name='county', 
    mapbox_style='white-bg', 
    color_continuous_scale=px.colors.diverging.Temps_r,
    zoom=5,
    center={"lat": 55, "lon": 0}, 
    animation_frame='date',
    range_color=[-1,1]
                           )

#  App Layout 
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Sentiment of Tweets about COVID-19 by UK region"),
            ],
        ),
        html.Div(
           dcc.Graph(
            id='example-graph-2',
            figure=fig_0
        )
        ),
    ],
)


# callback
# @app.callback(dash.dependencies.Output('display-value', 'children'),
#               [dash.dependencies.Input('dropdown', 'value')])
# def display_value(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)