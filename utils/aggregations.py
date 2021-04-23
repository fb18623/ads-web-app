import pandas as pd

score_columns = ['nn-score', 'vader-score', 'textblob-score']
prediction_columns = ['nn-predictions', 'vader-predictions', 'textblob-predictions']
sentiments = {'neg': -1, 'pos': 1, 'neu': 0}

sen

def aggregate_sentiment_by_region_type_by_date(data, region_list, region_header,
                                               start,
                                               end):
    """
    :param data:
    :param region_list:
    :param region_header:
    :param start:
    :param end:
    :return:
    DataFrame where each column is each region, each row is each date. Cells contain average sentiment/score of that region
    within specified date.

    """
    date_list = [str(date.date()) for date in pd.date_range(start=start, end=end).tolist()]
    sentiment_by_region = {'{}_avg_sentiment'.format(prediction_version): []
                           for prediction_version in prediction_columns}
    score_by_region = {'{}_avg_score'.format(prediction_version): [] for
                       prediction_version in prediction_columns}
    dates = []
    regions = []
    for date in date_list:
        date_data = data.loc[data['date'].str.contains(date)]
        for region in region_list:
            region_data = date_data.loc[date_data[region_header] == region]
            dates.append(date)
            regions.append(region)
            for i, prediction_version in enumerate(prediction_columns):
                score_version = score_columns[i]
                if not region_data.empty:
                    total_sentiment = sum([sentiments[region_data[prediction_version].values[0]]])
                    total_score = sum(region_data[score_version].values.tolist())
                    sentiment_by_region['{}_avg_sentiment'.format(prediction_version)].append(
                        total_sentiment / len(region_data.index))
                    score_by_region['{}_avg_score'.format(prediction_version)].append(
                        total_score / len(region_data.index))
                else:
                    sentiment_by_region['{}_avg_sentiment'.format(prediction_version)].append(0)
    full_data = pd.concat(
        [pd.DataFrame({'date': dates}), pd.DataFrame({'region_name': regions}), pd.DataFrame(sentiment_by_region),
         pd.DataFrame(score_by_region)], axis=1)
    return full_data
