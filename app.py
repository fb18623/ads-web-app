import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Sentiment Towards Lockdown in the UK'

# Read data
df_covid_stats = pd.read_csv('/Users/lily/PycharmProjects/web-app/data/COVID-Dataset/uk_covid_stats.csv')

# Make figures
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

#  App Layout 
app.layout = html.Div([
    html.H2('UK COVID-19 Twitter Sentiment'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in ['Lockdown', 'Covid']],
        value='Lockdown'
    ),
    html.Div(id='display-value'),

    html.H4(children='Daily Cases and Deaths'),
    generate_table(df_covid_stats)

    
])

@app.callback(dash.dependencies.Output('display-value', 'children'),
              [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)