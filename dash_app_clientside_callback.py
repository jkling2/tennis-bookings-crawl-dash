import datetime
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
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
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    for d in days:
        res.append({'label': d, 'value': d})
    return res


def round_down_to_full_quarter_minutes(day_time_to_round):
    return (pd.to_datetime(day_time_to_round) - pd.Timedelta(
        minutes=(int(pd.to_datetime(day_time_to_round).strftime('%M')) % 15))).strftime('%H:%M')


def make_fig(data):
    figs = {}
    for weekday, grouped_by_day in data.groupby("weekday"):
        fig = go.Figure()
        for playMode, grouped_by_mode in grouped_by_day.groupby("playMode"):
            fig.add_trace(
                go.Bar(x=grouped_by_mode["startTime"], y=grouped_by_mode["avgBooking"], name=playMode,
                       marker={'color': colors[playMode]}))
        fig.update_layout(legend_title_text="Buchungsart", barmode='stack', legend={'traceorder': 'normal'})
        fig.update_xaxes(title_text="Uhrzeit", fixedrange=True)
        fig.update_yaxes(title_text="Ø Reservierungen", range=[0, amount_courts], tick0=0, dtick=1,
                         fixedrange=True)
        figs[weekday] = fig
    return figs


df = load_prepare_data.load_prepare_csv()
days_d_to_en_dic = {"Montag": "Monday", "Dienstag": "Tuesday", "Mittwoch": "Wednesday", "Donnerstag": "Thursday",
                    "Freitag": "Friday", "Samstag": "Saturday", "Sonntag": "Sunday"}
days_en_to_d_dic = {v: k for k, v in days_d_to_en_dic.items()}
amount_courts = 15
current_date = datetime.datetime.now()
day = days_en_to_d_dic[pd.to_datetime(current_date).day_name()]
day_time = current_date.strftime('%H:%M')
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

colors = {'gesperrt': 'black',
          'Training': 'blue',
          'Einzel': 'green',
          'Einzel Flutlicht': 'limegreen',
          'Doppel': 'orange',
          'Doppel Flutlicht': 'gold',
          'Medenspiel': 'red'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(children=[
    dcc.Interval(
        id="load_interval",
        n_intervals=0,
        max_intervals=0,  # <-- only run once
        interval=1
    ),
    dbc.Row(
        [
            dbc.Col(xxl=3, xs=2),
            dbc.Col(html.H1(children='Platzbuchungen für TC BW Vaihingen-Rohr')),
            dbc.Col(xs=2),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(xxl=3, xs=2),
            dbc.Col(html.H2(id='h2')),
            dbc.Col(xs=2),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(xxl=3, xs=2),
            dbc.Col(dcc.Dropdown(id='day-picker',
                                 options=days_dic,
                                 clearable=False)),
            dbc.Col(dcc.Dropdown(id='time-picker',
                                 options=times,
                                 clearable=False)),
            dbc.Col(lg=5, md=4, sm=3, xs=2),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(xxl=3, xs=2),
            dbc.Col(dcc.Graph(id='avg-reservations-day-day-time',
                              style={"width": "90%"})),
            dbc.Col(xxl=3, xs=2),
        ]
    ),
    dcc.Store(id='store', data=make_fig(agg_data)),
    dcc.Store(id='days_d_to_en_dic', data=days_d_to_en_dic),
])


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_store_data_initial'
    ),
    Output('day-picker', 'value'),
    Output('time-picker', 'value'),
    Input(component_id="load_interval", component_property="n_intervals")
)


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_store_data'
    ),
    Output('avg-reservations-day-day-time', 'figure'),
    Output('h2', 'children'),
    Input('day-picker', 'value'),
    Input('time-picker', 'value'),
    State('store', 'data'),
    State('days_d_to_en_dic', 'data')
)


if __name__ == '__main__':
    app.run_server(debug=False)
