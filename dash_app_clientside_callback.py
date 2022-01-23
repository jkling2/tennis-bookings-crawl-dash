import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
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
                go.Bar(x=grouped_by_mode["startTime"], y=grouped_by_mode["avgBooking"], name=playMode, marker={'color': colors[playMode]}))
        fig.update_layout(legend_title_text="Buchungsart", barmode='stack', legend={'traceorder':'normal'})
        fig.update_xaxes(title_text="Uhrzeit", fixedrange=True)
        fig.update_yaxes(title_text="Durchschnittliche # Buchungen", range=[0, amount_courts], tick0=0, dtick=1, fixedrange=True)
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

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Platzbuchungen für TC BW Vaihingen-Rohr'),
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
    ),
    dcc.Store(id='store', data=make_fig(agg_data)),
    dcc.Store(id='days_d_to_en_dic', data=days_d_to_en_dic),
])


app.clientside_callback(
    """
    function(reference_day_time, reference_day, store_data, days_d_to_en_dic) {
        var start_times = [];
        var dt = new Date();
        dt.setHours(reference_day_time.split(':')[0]);
        dt.setMinutes(reference_day_time.split(':')[1] - 30);
        for (let s = 0; s <= 6; s++) {
            start_times.push(dt.getHours() + ":" + (dt.getMinutes() < 10 ? '0' + dt.getMinutes() : dt.getMinutes()));
            dt.setMinutes(dt.getMinutes() + 15);
        }
        let day_data = store_data[days_d_to_en_dic[reference_day]];
        let data_for_day_time = {};
        data_for_day_time['layout'] = day_data['layout'];
        let data = [];
        for (let m = 0; m < day_data['data'].length; m++) {
            let mode = day_data['data'][m];
            let mode_for_day_time = {};
            mode_for_day_time['marker'] = mode['marker']
            mode_for_day_time['name'] = mode['name']
            mode_for_day_time['type'] = mode['type']
            let data_y = [].fill(0.0);
            for (let i = 0; i < mode['x'].length; i++) {
                let idx = start_times.indexOf(mode['x'][i]);
                if (idx >= 0) {
                    data_y[idx] = mode['y'][i];
                }
            }
            mode_for_day_time['x'] = [];
            for (let s = 0; s < start_times.length; s++) {
                if (s == 2) {
                    mode_for_day_time['x'].push("<b>" + start_times[s] + "</b>");
                } else {
                    mode_for_day_time['x'].push(start_times[s]);
                }
            }
            mode_for_day_time['y'] = data_y;
            data.push(mode_for_day_time);
        }
        data_for_day_time['data'] = data;
        return [data_for_day_time, `Durchschnittliche Reservierungen für ${reference_day} gegen ${reference_day_time} Uhr`];
    }
    """,
    Output('avg-reservations-day-day-time', 'figure'),
    Output('h2', 'children'),
    Input('time-picker', 'value'),
    Input('day-picker', 'value'),
    State('store', 'data'),
    State('days_d_to_en_dic', 'data')
)


if __name__ == '__main__':
    app.run_server(debug=True)
