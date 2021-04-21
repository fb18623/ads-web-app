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

# -------- Plotting map ------- #
uk_counties = json.load(open('uk_counties_simpler.json', 'r'))
geo_df = pd.read_csv('year_data.csv')
start_time = datetime.datetime.now()
print('Plotting ' + str(len(geo_df)) + ' points.')
print('Plotting started')
date = '2020-03-20'
geo_df = geo_df.loc[geo_df['date'] == date]
fig = px.choropleth_mapbox(
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

fig.show()
end_time = datetime.datetime.now()
print('Done. Time take to plot is {}.'.format(end_time-start_time))
