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
# Make daily map
# --------- GEOJSON ---------- #
uk_counties = json.load(open('../data/Geojson/Ceremonial_counties.json', 'r'))
extra_counties = json.load(open('../data/Geojson/Counties_and_Unitary_Authorities_(December_2017)_Boundaries_in_the_UK_(WGS84) (1).json', 'r'))
norther_ireland = json.load(open('../data/Geojson/OSNI_Open_Data_-_50K_Boundaries_-_NI_Counties.json', 'r'))
area = {}  # Dictionary to map ID's from geojson data to a dataframe to plot
counter = 0  # Counter to assign ID's
name = 'NAME'  # Key that retrieves county names from geojson
topic = 'lockdown'

print('1')
def add_missing_counties(uk_counties, extra_counties, name, norther_ireland):  # Adding cornwall and dorset to geojson
    extra_counties_needed = ['Dorset', 'Cornwall']
    for feature in extra_counties['features']:
        if feature['properties']['ctyua17nm'] in extra_counties_needed:
            feature['properties'][name] = feature['properties']['ctyua17nm']
            feature['properties']['SHAPE_Leng'] = feature['properties']['st_lengths']
            feature['properties']['SHAPE_Area'] = feature['properties']['st_areasha']
            feature['properties']['OBJECTID'] = feature['properties']['objectid']
            uk_counties['features'].append(feature)
    for feature in norther_ireland['features']:
        feature['properties'][name] = feature['properties']['CountyName']
        uk_counties['features'].append(feature)
    return uk_counties


uk_counties = add_missing_counties(uk_counties, extra_counties, name, norther_ireland)
geo_list = []  # Used later to find counties within the twitter data that are unused
for feature in uk_counties['features']:
    feature['properties']['id'] = counter
    area[feature['properties'][name]] = feature['properties']['id']
    geo_list.append(feature['properties'][name])
    counter += 1


# ---------- Assigning counties and unitary authorities found in geojson to counties in twitter data ------- #
# geojson name : twitter name
key_map={'City and County of the City of London': 'Greater London',
         'Tyne & Wear': 'Tyne and Wear',
         'Western Isles': 'Eilean Siar',
         'Mid Glamorgan': 'Glamorgan',
         'West Glamorgan': 'Glamorgan',
         'South Glamorgan': 'Glamorgan',
         'Gwent': 'Monmouthshire',
         'Caithness': 'Highland',
         'Sutherland': 'Highland',
         'Nairn': 'Highland',
         'Ross and Cromarty': 'Highland',
         'Inverness': 'Highland',
         'City of Glasgow': 'Glasgow City',
         'Orkney': 'Orkney Islands',
         'Clackmannan': 'Clackmannanshire',
         'City of Dundee': 'Dundee City',
         'City of Aberdeen': 'Aberdeen City',
         'Berkshire': 'West Berkshire',
         'Shetland': 'Shetland Islands',
         'Bristol': 'Gloucestershire',
         'Berwickshire': 'Scottish Borders',
         'Tweeddale': 'Scottish Borders',
         'Roxburgh, Ettrick and Lauderdale': 'Scottish Borders',
         'Banffshire': 'Aberdeenshire',
         'Gwynedd': 'Anglesey',
         'Wigtown': 'Dumfries and Galloway',
         'Dumfries': 'Dumfries and Galloway',
         'The Stewartry of Kirkcudbright': 'Dumfries and Galloway',
         'Kincardineshire': 'Aberdeenshire',
         'ANTRIM': 'Antrim',
         'DOWN': 'Down',
         'FERMANAGH': 'Fermanagh',
         'ARMAGH': 'Armagh',
         'TYRONE': 'Tyrone',
         'LONDONDERRY': 'Derry and Londonderry'
        }

print('2')
# -------Welsh/Scottish county issue--------- #
# The changing twitter location into suitable locations
name_change_dict = {'Powys': ['Breconshire', 'Montgomeryshire', 'Radnorshire'],
                    'Renfrewshire': ['East Renfrewshire', 'Inverclyde'],
                    'Dunbartonshire': ['West Dunbartonshire', 'East Dunbartonshire'],
                    'Lanarkshire': ['North Lanarkshire', 'South Lanarkshire'],
                    'Ayrshire and Arran': ['South Ayrshire', 'East Ayrshire', 'North Ayrshire'],
                    'Dyfed': ['Carmarthenshire', 'Pembrokeshire'],
                    'Durham': ['Cleveland'],
                    'Clwyd': ['Flintshire', 'Denbighshire'],
                    'Gwynedd': ['Anglesey', 'Merionethshire'],
                    'Stirling and Falkirk': ['Falkirk', 'Stirling']
                    }

# -------Dataframe-------------- #
file_name = '../data/lockdown/daily_sentiment.csv'
predict_head = 'nn-predictions'
region_header = 'county'
columns = ['date', region_header, predict_head]
df = pd.read_csv(file_name, skipinitialspace=True, usecols=columns)
sentiments = {'neg': -1, 'pos': 1, 'neu': 0}
start_date = '2020-03-20'
end_date = '2021-03-25'


# Aggregating dataframe and county name changes
def agg_df(df, name_change_dict, sentiments, geo_list, predict_head, region_header, start_date, end_date):
    df['prediction'] = df[predict_head].apply(lambda x: sentiments[x])  # changing sentiment str to ints
    for key in name_change_dict:
        for county in name_change_dict[key]:  # changing counties in wales into powys district for plotting
            df[region_header] = np.where((df.county == county), key, df.county)

    region_list = df[region_header].unique()  # List of all unique county names in twitter data

    # Creating a dataframe with aggregated data for each county and date
    date_list = [str(date.date()) for date in pd.date_range(start=start_date, end=end_date).tolist()]
    total_arr = []
    used = []  # Has the twitter location been used
    for date in date_list:
        date_data = df.loc[df['date'].str.contains(date)]
        for region in region_list:
            region_data = date_data.loc[date_data[region_header] == region]
            if not region_data.empty:
                mean_sentiment = region_data['prediction'].mean()
                temp_arr = [date, region, mean_sentiment]
            else:
                temp_arr = [date, region, 0]
            if region in geo_list:
                used.append(1)
            else:
                used.append(0)
            total_arr.append(temp_arr)

    twitter_df = pd.DataFrame(data=total_arr, columns=['date', region_header, 'sentiment'])
    twitter_df['used'] = used

    return twitter_df


# Creates a dataframe with all geojson locations
def geojson_df(twitter_df, uk_counties, area, key_map, start_date, end_date, region_header):
    date_list = [str(date.date()) for date in pd.date_range(start=start_date, end=end_date).tolist()]
    total_arr = []
    list_loc = twitter_df[region_header].unique()
    for date in date_list:
        for i in range(len(uk_counties['features'])):
            region = uk_counties['features'][i]['properties'][name]
            if region in list_loc:  # If location exists within twitter dataframe
                value = twitter_df.loc[twitter_df[region_header] == region].loc[twitter_df['date'] == date][
                    'sentiment'].mean()
                new_county = region  # For comparison between actual county and county data used
                twitter_df.loc[twitter_df[region_header] == region, 'used'] = 1
                viable = 1
            else:  # If location does not exist within twitter dataframe
                if region in key_map:  # If location exists with key map, therefore can be assigned a county from twitter data
                    key = key_map[region]
                    new_county = key  # For comparison between actual county and county data used
                    value = twitter_df.loc[twitter_df[region_header] == key]['sentiment'].mean()
                    twitter_df.loc[twitter_df[region_header] == key, 'used'] = 1
                    viable = 1
                else:  # Cannot find a viable county
                    new_county = region  # For comparison between actual county and county data used
                    value = 0
                    viable = 0

            total_arr.append([date, region, value, new_county, viable])

    geo_df = pd.DataFrame(data=total_arr, columns=['date', region_header, 'sentiment', 'New County', 'viable'])  # same dataframe layout as above using geo locations
    geo_df['id'] = geo_df[region_header].apply(lambda x: area[x])  # Adding ID's to datafarme for plotting

    return geo_df

def create_geo_df():
    twitter_df = agg_df(df, name_change_dict, sentiments, geo_list, predict_head, region_header, start_date, end_date)
    geo_df = geojson_df(twitter_df, uk_counties, area, key_map, start_date, end_date, region_header)
    geo_df = geo_df.sort_values('id')
    geo_df = geo_df.fillna(0)  # If a county doesn't exist within the twitter data it is given a NaN value. This makes it 0.
    print(geo_df.head())
    geo_df.drop(columns=['New County', 'viable'])
    print(geo_df.tail())

    twitter_df = twitter_df.sort_values('county')

    # Unassigned values mean there should exist a county within the twitter data for which the geo location can relate.
    print('There are ' + str(len(twitter_df[twitter_df.used == 0]['county'].unique())) + ' locations not used within the twitter data')
    print(twitter_df[twitter_df.used == 0]['county'].unique())
    print('There are ' + str(len(geo_df['New County'].unique())) + ' different locations within the geojson data')
    print('There are ' + str(len(geo_df[geo_df.viable == 0]['county'].unique())) + ' locations with unnassigned values.')
    print(geo_df[geo_df.viable == 0]['New County'].unique())

    geo_df.to_csv('../data/{}}_tweets.csv'.format(topic))
# with open('uk_counties.json', 'w') as f:
#     json.dump(uk_counties, f)
# # -------- Plotting map ------- #
# start_time = datetime.datetime.now()
# print('Plotting ' + str(len(geo_df)) + ' points.')
# print('Plotting started')
# fig = px.choropleth_mapbox(geo_df, 
# locations="id", 
# featureidkey='properties.id', 
# geojson=uk_counties,
# color='sentiment', 
# hover_name=region_header, 
# mapbox_style='white-bg', 
# zoom=5,
# center={"lat": 55, "lon": 0}, 
# # animation_frame='date'
#                            )
# fig.show()
# end_time = datetime.datetime.now()
# print('Done. Time take to plot is {}.'.format(end_time-start_time))
