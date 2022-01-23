import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd

import load_prepare_data


def calculate_times_options():
    res = []
    end_time = pd.to_datetime('23:00')
    start_time = pd.to_datetime('07:00')
    while start_time <= end_time:
        res.append({'label': start_time.strftime('%H:%M'), 'value': start_time.strftime('%H:%M')})
        start_time += pd.Timedelta(minutes=15)
    return res


def calculate_days_options():
    res = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for d in days:
        res.append({'label': d, 'value': d})
    return res


def calculate_start_times(ref_day_time, n_bef, n_aft):
    res = []
    curr_time = pd.to_datetime(ref_day_time)
    start_time = curr_time - pd.Timedelta(minutes=(int(curr_time.strftime('%M')) % 15))
    res.append(start_time.strftime('%H:%M'))
    for i in range(n_bef):
        time_to_add = start_time - pd.Timedelta(minutes=(i + 1) * 15)
        res.append(time_to_add.strftime('%H:%M'))
    for i in range(n_aft):
        time_to_add = start_time + pd.Timedelta(minutes=(i + 1) * 15)
        res.append(time_to_add.strftime('%H:%M'))
    return res


def round_down_to_full_quarter_minutes(day_time_to_round):
    return (pd.to_datetime(day_time_to_round) - pd.Timedelta(
        minutes=(int(pd.to_datetime(day_time_to_round).strftime('%M')) % 15))).strftime('%H:%M')


df = load_prepare_data.load_prepare_csv()
amount_courts = 15
current_date = datetime.datetime.now()
day = pd.to_datetime(current_date).day_name()
day_time = current_date.strftime('%H:%M')
n_before = 2
n_after = 4
times = calculate_times_options()
days_dic = calculate_days_options()
data_per_weekday = df.groupby('weekday')['date'].unique().reset_index(name='uniqueDates').set_index('weekday')
data_per_weekday['amountDates'] = data_per_weekday['uniqueDates'].str.len()
data_per_weekday.drop(columns=['uniqueDates'], inplace=True)
data_per_weekday['amountPossibleBookingsPerStartTime'] = data_per_weekday['amountDates'] * amount_courts
# display average reservations for day's day time
agg_data = df.groupby(['playMode', 'startTime', 'weekday']).size().reset_index(name='n')
agg_data = agg_data.merge(data_per_weekday, on='weekday')
agg_data['avgBooking'] = agg_data['n'] / agg_data['amountPossibleBookingsPerStartTime'] * amount_courts

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Booking data for TC BW Vaihingen-Rohr'),
    html.H2(id='h2'),
    html.Div([
        dcc.Dropdown(id='day-picker',
                     options=days_dic,
                     value=day,
                     clearable=False,
                     style=dict(
                         width='80%'
                     )),
        dcc.Dropdown(id='time-picker',
                     options=times,
                     value=round_down_to_full_quarter_minutes(day_time),
                     clearable=False,
                     style=dict(
                         width='80%'
                     )),
    ], style=dict(display='flex', width='20%', )),
    dcc.Graph(
        id='avg-reservations-day-day-time',
        style=dict(
            width='40%',
            verticalAlign="middle"
        )
    )
])


@app.callback(
    Output('avg-reservations-day-day-time', 'figure'),
    Output('h2', 'children'),
    Input('time-picker', 'value'),
    Input('day-picker', 'value'))
def update_figure(reference_day_time, reference_day):
    start_times = calculate_start_times(reference_day_time, n_before, n_after)
    start_times.sort()
    day_data = agg_data.loc[(agg_data['weekday'] == reference_day) & (agg_data['startTime'].isin(start_times))]
    fig = px.bar(day_data, x='startTime', y='avgBooking', color='playMode',
                 color_discrete_map={'gesperrt': 'black',
                                     'Training': 'blue',
                                     'Einzel': 'green',
                                     'Einzel Flutlicht': 'limegreen',
                                     'Doppel': 'orange',
                                     'Doppel Flutlicht': 'gold',
                                     'Medenspiel': 'red'},
                 labels={'startTime': 'Uhrzeit',
                         'avgBooking': 'Durchschnittliche # Buchungen',
                         'playMode': 'Buchungsart'
                         },
                 title='Durchschnittliche Anzahl an Buchungen pro Tageszeit'
                 )
    fig.update_layout(yaxis_range=[0, amount_courts])
    fig.update_yaxes(tick0=0, dtick=1)
    return fig, 'Average reservations for ' + reference_day + ' around ' + reference_day_time


if __name__ == '__main__':
    app.run_server(debug=True)
