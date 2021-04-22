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
from dash.dependencies import Input, Output
import plotly.figure_factory as ff

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Sentiment Towards Lockdown in the UK'

# Read data
df_covid_stats = pd.read_csv('data/COVID-Dataset/uk_covid_stats.csv')
uk_counties = json.load(open('data/Geojson/uk_counties_simpler.json', 'r'))
geo_df = pd.read_csv('data/year_data.csv')
dates_list = pd.date_range(start="2020-03-20", end="2021-03-19").tolist()

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
    zoom=3.5,
    center={"lat": 55, "lon": 0},
    animation_frame='date',
    range_color=[-1, 1],
)

# initial news articles
date = '2020-03-20'
news_df = pd.read_csv('data/news_timeline.csv')
news_df = news_df.loc[news_df['Date'] == date]
news_fig = ff.create_table(news_df.drop('Date', 1))

#  App Layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(
                    children="Sentiment of Tweets about COVID-19 in the UK by County"),
            ],
        ),

        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the date:",
                                ),
                                dcc.Slider(
                                    id="days-slider",
                                    min=0,
                                    max=364,
                                    value=0,
                                    marks={
                                        str(x): {
                                            "label": dates_list[x].date()
                                        }
                                        for x in range(0, 364, 30)
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of sentiment towards lockdown in the UK on day: ",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id='county-choropleth',
                                    figure=fig_0
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="daily-news",
                    children=[
                           html.H6(
                    children="On this day in the news..."),
                       dcc.Graph(
                        id='news-table',
                            figure=news_fig
                        ),

                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Moving Average",
                                    "value": "show_mmoving_average",
                                },
                                {
                                    "label": "Emoji Sentiment",
                                    "value": "show_emoji_sentiment",
                                },
                                {
                                    "label": "COVID Sentiment vs Time",
                                    "value": "show_sentiment_vs_time",
                                },
                            ],
                            value="show_death_rate_single_year",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(

                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(Output("heatmap-title", "children"), [Input("days-slider", "value")])
def update_map_title(date):
    return "Heatmap of sentiment towards lockdown in the UK on the day: {0}".format(
        dates_list[date].date()
    )


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("days-slider", "value")],
)
def display_map(day):
    uk_counties = json.load(open('data/Geojson/uk_counties_simpler.json', 'r'))
    geo_df = pd.read_csv('data/year_data.csv')
    # Initial map
    date = str(dates_list[day].date())
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
        zoom=3.5,
        center={"lat": 55, "lon": 0},
        animation_frame='date',
        range_color=[-1, 1],
    )
    return fig

@app.callback(
    Output("news-table", "figure"),
    [Input("days-slider", "value")],
)
def display_news(day):
    date = str(dates_list[day].date())
    news_df = pd.read_csv('data/news_timeline.csv')
    news_df = news_df.loc[news_df['Date'] == date]
    news_fig = ff.create_table(news_df.drop('Date', 1))
    return(news_fig)

if __name__ == '__main__':
    app.run_server(debug=True)
