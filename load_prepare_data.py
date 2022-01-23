from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

booking_data_json_path = "data/bookingData.json"
booking_data_csv_path = "data/bookingData.csv"

def load_prepare_JSON():
    # read raw data
    df = pd.read_json(booking_data_json_path, 'records').explode('reservations')
    print(df.shape)
    # get relevant data (reservations), flatten JSON and get relevant columns
    df = pd.json_normalize(df['reservations'].dropna())[['court', 'date', 'fromTime', 'toTime', 'text', 'shortText', 'info', 'additionalPlayers']]
    # drop data after first week of November
    df = df.loc[pd.to_datetime(df['date'], format='%d.%m.%Y').dt.date < datetime(2021, 10, 9).date()]
    print(df.shape)
    # add weekday column
    df['weekday'] = pd.to_datetime(df['date'], format='%d.%m.%Y').dt.day_name()
    # correct court number
    df['court'] = df['court']-1210
    # split info to determine players and play mode
    df['playerCount'] = df['additionalPlayers'].str.len() + 1
    df['guestPlayerCount'] = df['additionalPlayers'].apply(lambda l : np.count_nonzero(["Gast" in dic['text'] for dic in l]))
    df['playMode'] = df['info'].str.split(' • ').str[-1]
    df.loc[df['text'].str.lower() == 'gesperrt', 'playMode'] = 'gesperrt'
    # calculate start times (a session starts every 15 minutes) and explode one starttime per line
    df['startTime'] = df.apply(lambda row : calc_times(pd.to_datetime(row.fromTime, format='%H:%M'),
                                                       pd.to_datetime(row.toTime, format='%H:%M')), axis=1)
    df = df.explode('startTime')
    # drop not needed columns
    df.drop(columns=['fromTime', 'toTime', 'text', 'shortText', 'info', 'additionalPlayers'], inplace=True)
    df.to_csv(booking_data_csv_path)
    print(df.shape)
    print(df.dtypes)
    print(df.head())
    return df


def load_prepare_csv():
    return pd.read_csv(booking_data_csv_path)


def aggregate_data(df):
    df_bookable_courts = df.loc[df['playMode'].str.lower() != 'gesperrt']
    # aggregate reservations per day time
    agg_start_time = df_bookable_courts.groupby('startTime').size()
    agg_start_time = agg_start_time.reset_index(name='n')
    print(agg_start_time.shape)
    print(agg_start_time)

    # aggregate reservations per day and day time
    agg_start_time_per_week_day_sum = df_bookable_courts.groupby(['weekday', 'startTime']).size().reset_index(name='n')
    color_map = {'Monday': 'red', 'Tuesday': 'blue', 'Wednesday': 'green', 'Thursday': 'orange', 'Friday': 'brown', 'Saturday': 'gray', 'Sunday': 'yellow'}
    colors = agg_start_time_per_week_day_sum['weekday'].apply(lambda x: color_map[x])
    agg_start_time_per_week_day_sum['x'] = agg_start_time_per_week_day_sum['weekday'] + " - " + agg_start_time_per_week_day_sum['startTime']
    agg_start_time_per_week_day_sum.plot.bar(x='x', y='n', color=colors)
    print(agg_start_time_per_week_day_sum.shape)
    print(agg_start_time_per_week_day_sum)

    agg_date_start_time = df_bookable_courts.groupby(['date', 'weekday', 'startTime']).size().reset_index(name='n')
    # average reservations per day time
    agg_start_time_avg = agg_date_start_time.groupby('startTime')['n'].mean()
    agg_start_time_avg.plot.bar()
    print(agg_start_time_avg.shape)
    print(agg_start_time_avg)

    # average reservations per day and day time
    agg_start_time_per_week_day_avg = agg_date_start_time.groupby(['startTime', 'weekday'])['n'].mean()
    agg_start_time_per_week_day_avg.plot.bar()
    plt.show()
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    agg_start_time_per_week_day_avg = agg_start_time_per_week_day_avg.reset_index(name='n')
    print(agg_start_time_per_week_day_avg.shape)
    print(agg_start_time_per_week_day_avg)
    for day in days:
        day_data = agg_start_time_per_week_day_avg.loc[agg_start_time_per_week_day_avg['weekday'] == day]
        day_data.plot.bar(x='startTime', y='n')
        plt.show()

    # display total time a court was not bookable
    non_bookable_courts = df.loc[df['playMode'].str.lower() == 'gesperrt'].groupby('court').size().reset_index(name='n')
    non_bookable_courts['time(h)'] = non_bookable_courts['n'] * 15 / 60
    non_bookable_courts.plot.bar(x='court', y='time(h)')
    plt.show()
    print(non_bookable_courts.shape)
    print(non_bookable_courts)


def calc_times(from_time, to_time):
    res = []
    start_time = from_time
    while start_time < to_time:
        res.append(start_time.strftime('%H:%M'))
        start_time += pd.Timedelta(minutes=15)
    return res


if __name__ == '__main__':
    load_prepare_JSON()
    aggregate_data(load_prepare_csv())