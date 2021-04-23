import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
pd.options.mode.chained_assignment = None  # Removes copy warning
from utils.aggregations import aggregate_sentiment_by_region_type_by_date
# Replace lines 10-12 with local directory for twitter data.
# Replace lines 13-20 with the country to plot, column names for data and date range.

file_name_sent = '../data/{}/all_tweet_sentiments.csv'
file_name_stats = '../data/COVID-Dataset/uk_covid_stats.csv'
file_name_num_tweet = '../data/{}/daily_tweet_count_country.csv'
file_name_key_events = '../data/events/key_events.csv'
case_str = 'newCasesByPublishDate'
death_str = 'newDeathsByDeathDate'
event_str = 'Event'
countries = ['England', 'Scotland', 'Northern Ireland', 'Wales']
counties = pd.read_csv('../data/Geojson/uk-district-list-all.csv')['county'].tolist()
regions_lists = {'county':counties, 'country':countries}


# -------Dataframe-------------- #
def create_df(topic, sentiment_type, region_type, start, end):
    df_sent = pd.read_csv(file_name_sent.format(topic), skipinitialspace=True)
    df_agg = aggregate_sentiment_by_region_type_by_date(df_sent, regions_lists[region_type], region_type, start, end)
    df_stats = pd.read_csv(file_name_stats, skipinitialspace=True, usecols=['date', 'country', death_str, case_str])
    df_num_tweet = pd.read_csv(file_name_num_tweet.format(topic), skipinitialspace=True,
                               usecols=['date', 'England', 'Scotland', 'Northern Ireland', 'Wales'])
    df_events = pd.read_csv(file_name_key_events, skipinitialspace=True, usecols=['Date', event_str])
    return df_agg, df_stats, df_num_tweet, df_events


def create_event_array(df_events, start, end, event):
    date_list = [str(date.date().strftime('%d/%m/%Y')) for date in pd.date_range(start=start, end=end).tolist()]
    event_arr = []
    for date in date_list:
        if date in df_events['Date'].unique():
            event = df_events.loc[df_events['Date'] == date][event]
            event_arr.append(event.values[0])
        else:
            event_arr.append('')

    return event_arr


def date_range(start, end, df_sent, df_stats, df_num_tweet):
    date_list = [str(date.date()) for date in pd.date_range(start=start, end=end).tolist()]
    df_stats = df_stats.reindex(index=df_stats.index[::-1])  # Flipping df as dates are wrong way round (needed for MA)
    df_sent = df_sent.loc[df_sent['date'].isin(date_list)]
    df_stats = df_stats.loc[df_stats['date'].isin(date_list)]
    df_num_tweet = df_num_tweet.loc[df_num_tweet['date'].isin(date_list)]

    return df_sent, df_stats, df_num_tweet


# MA calculated during splitting of dataframes
def split_df(df_sent, df_stats, region_type, df_num_tweet, sentiment_type, MA_win=7):
    region_df_sent_dict = {}
    region_df_stats_dict = {}
    sentiment_avg_col = sentiment_type+'_avg_score'
    for region in df_sent['region_name'].unique():
        df_num_tweet.loc[:, region] = df_num_tweet.loc[:, region].rolling(window=MA_win).mean().dropna()  #7 Day MA
        temp_sent = df_sent.loc[df_sent['region_name'] == region]  # Splitting DF into countries
        print(temp_sent.columns)
        temp_stats = df_stats.loc[df_stats[region_type] == region]
        temp_sent.loc[:, sentiment_type] = temp_sent.loc[:, sentiment_type].rolling(window=MA_win).mean().dropna()  #7 Day MA
        temp_stats.loc[:, [death_str, case_str]] = temp_stats.loc[:, [death_str, case_str]].rolling(window=MA_win).mean().dropna()
        region_df_sent_dict[region] = temp_sent.dropna()
        region_df_stats_dict[region] = temp_stats.dropna()
    return region_df_sent_dict, region_df_stats_dict


def plot(topic, sentiment_type, region_type, country,  start, end):
    df_sent, df_stats, df_num_tweet, df_events = create_df(topic, sentiment_type, region_type, start ,end)
    df_sent, df_stats, df_num_tweet = date_range(start, end, df_sent, df_stats, df_num_tweet)

    region_df_sent_dict, region_df_stats_dict = split_df(df_sent, df_stats, region_type,
                                                         df_num_tweet, sentiment_type)
    event_arr = create_event_array(df_events, start, end, event_str)
    fig = make_subplots(rows=2, cols=1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                        subplot_titles=("Number of tweets and sentiment", "Spread of the virus"))
    fig.add_trace(
        go.Scatter(x=region_df_sent_dict[country]['date'], y=region_df_sent_dict[country][sentiment_type],
                   name="7 Day MA: Sentiment", text=event_arr, textposition="bottom center"), secondary_y=False,
        row=1, col=1,)
    fig.add_trace(
        go.Scatter(x=df_num_tweet['date'], y=df_num_tweet[country],
                   name="7 Day MA: Number of Tweets", text=event_arr, textposition="bottom center"), secondary_y=True,
        row=1, col=1,)
    fig.add_trace(
        go.Scatter(x=region_df_stats_dict[country]['date'], y=region_df_stats_dict[country][case_str],
                   name="7 Day MA: Covid Cases", text=event_arr, textposition="bottom center"), secondary_y=False,
        row=2, col=1,)
    fig.add_trace(
        go.Scatter(x=region_df_stats_dict[country]['date'], y=region_df_stats_dict[country][death_str],
                   name="7 Day MA: Covid Deaths", text=event_arr, textposition="bottom center"), secondary_y=True,
        row=2, col=1,)

    fig.update_layout(title_text=country)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Sentiment", secondary_y=False, row=1, col=1)
    fig.update_yaxes(title_text="Number of Tweets", secondary_y=True, row=1, col=1)
    fig.update_yaxes(title_text="Covid Cases", secondary_y=False, row=2, col=1)
    fig.update_yaxes(title_text="Covid Deaths", secondary_y=True, row=2, col=1)
    fig.show()


plot('covid', 'nn-predictions', 'country', 'England', '2020-03-20', '2020-03-25')