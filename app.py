import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
import plotly
import json
from flask import Flask, render_template, request
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import repeat

app = Flask(__name__)


def fetch_air_quality(borough):
    all_files = glob.glob("data/Data_{0}*.csv".format(borough))

    #     df_bexley = pd.DataFrame(columns = ['Year'])
    df_borough = pd.DataFrame(columns=['MeasurementDateGMT'])
    # print(all_files)
    for filename in all_files:
        # print(filename)
        df_data = pd.read_csv(filename)
        df_data_borough = df_data[df_data.columns[1:]].rename(
            columns=lambda x: x.split(':')[1])
        df_data_borough['MeasurementDateGMT'] = df_data['MeasurementDateGMT']
        df_borough = df_borough.reset_index()
        df_borough = pd.concat([df_borough, df_data_borough])
        df_borough = df_borough.groupby('MeasurementDateGMT').mean()

        df_borough.index = pd.to_datetime(df_borough.index)
    # print(df_borough)
    print(borough)
    df_borough = df_borough.groupby(pd.Grouper(freq='W')).mean()
    #     df_borough = df_borough.groupby('MeasurementDateGMT').sum()
    df_borough.index = pd.to_datetime(df_borough.index)
    df_borough = df_borough.rename(columns={' Nitric Oxide (ug/m3)': 'NO',
                                            ' Nitrogen Dioxide (ug/m3)': 'NO2',
                                            ' Oxides of Nitrogen (ug/m3)':
                                                'NOX',
                                            ' Ozone (ug/m3)': 'O3',
                                            ' PM10 Particulate (ug/m3)': 'PM10',
                                            ' PM2.5 Particulate (ug/m3)': 'PM25',
                                            ' Sulphur Dioxide (ug/m3)': 'SO2',
                                            ' Carbon Monoxide (mg/m3)': 'CO'})

    return df_borough


def fetch_min_air_pollutant(borough_name):
    df_data = fetch_air_quality(borough_name)
    df_data['date'] = df_data.index

    col_list = ['AirPollutant', 'Date', 'Value']
    df_min_air = pd.DataFrame(columns=col_list)

    for col in df_data:
        if col == 'date':
            continue
        # data = df_data[df_data[col] == df_data[col].min()]
        data = df_data.loc[[df_data.loc[df_data[col] > 0, col].idxmin()]]
        air_date = pd.to_datetime(data.date).dt.date
        val = data[col].values[0]
        val = round(val, 2)
        data_list = [col, air_date[0], val]
        print(data_list)
        df = pd.DataFrame([data_list], columns=col_list)
        df_min_air = df_min_air.append(df)
    #     df['Value'].round(decimals=2)
    df_min_air.set_index('AirPollutant', inplace=True)
    return df_min_air

def plot_line_air_pollutant(borough_name):

    # df_data = fetch_air_quality(borough_name)
    df_data = pd.read_csv('data_mean/data_borough/{}.csv'.format(borough_name))
    df_data['date'] = df_data.MeasurementDateGMT
    df_data = df_data.drop(['MeasurementDateGMT'], axis=1)
    # df_data['date'] = df_data.index
    df_data_wo_date = df_data.drop(['date'], axis=1)
    max_range = df_data_wo_date.max().max()

    fig = go.Figure(
        layout=go.Layout(
            updatemenus=[
                dict(type="buttons", direction="right", x=1.0, y=1.25), ],
            xaxis=dict(range=["2018-01-01", "2021-06-16"],
                       autorange=False, tickwidth=2,
                       title_text="Time"),
            yaxis=dict(range=[0, max_range],
                       autorange=False,
                       title_text="Value (ug/m3)"),
            title="Air Pollutant Timeline",
        ))

    # Add traces
    init = 1

    color_list = ['#00ffbf', '#ffbf00', '#bfff00', '#bf00ff', '#00bfff',
                  '#00ff80', '#ff8000', '#00ff80']

    color_dict = {'NO': '#EF9A9A', 'NO2': '#CE93D8', 'NOX': '#90CAF9',
                  'O3': '#A5D6A7', 'PM10': '#E6EE9C',
                  'PM25': '#BCAAA4', 'SO2': '#ff944d', 'CO': '#4d4d33'}

    i = 0
    for col in df_data.columns:
        if col == 'date':
            continue
        i = i + 1
        fig.add_trace(
            go.Scatter(x=df_data.date[:init],
                       y=df_data[col][:init],
                       name=col,
                       visible=True,
                       line=dict(color=color_dict.get(col))))  

    # Animation
    frame_list = []

    for k in range(init, len(df_data) + 1):

        animation_list = []
        for col in df_data.columns:
            animation_list.append(
                go.Scatter(x=df_data.date[:k], y=df_data[col][:k]))
        frame_list.append(go.Frame(data=animation_list))
    # print(frame_list)

    fig.update(frames=frame_list)

    # Extra Formatting
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='white',
                     ticklen=10,mirror=True,showline=True)
    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=1,mirror=True,showline=True)
    fig.update_layout(yaxis_tickformat=',')
    fig.update_layout(legend=dict(x=0, y=1.12), legend_orientation="h")
    fig.add_vline(x='2019-04-08')
    fig.add_annotation(x='2019-03-28',
                       text="Start of ULEZ (11th April, 2019)",
                       showarrow=False, textangle=-90)
    fig.add_vrect(x0="2020-03-23", x1="2020-06-01",
                  fillcolor="Grey", opacity=0.5, line_width=0)
    fig.add_annotation(x='2020-04-30',
                       text="Covid-19 First Lockdown",
                       showarrow=False, textangle=-90)
    fig.add_vrect(x0="2020-11-05", x1="2020-12-02",
                  fillcolor="Grey", opacity=0.5, line_width=0)
    fig.add_annotation(x='2020-11-18',
                       text="Covid-19 Second Lockdown",
                       showarrow=False, textangle=-90)
    fig.add_vrect(x0="2021-01-06", x1="2021-07-04",
                  fillcolor="Grey", opacity=0.5, line_width=0)
    fig.add_annotation(x='2021-03-25',
                       text="Covid-19 Third Lockdown",
                       showarrow=False, textangle=-90)

    # Buttons

    button_list = []
    button_list.append(dict(label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 1000},"transition": {"duration": 0}}]))

    visible_list = [False] * (len(df_data.columns) - 1)
    i = 0

    for col in df_data.columns:
        if col == 'date':
            continue
        visible_list[i] = True
        button_list.append(dict(label=col,
                                method="update",
                                args=[{"visible": visible_list[:]},
                                      {"showlegend": True}]))

        visible_list[i] = False
        i = i + 1

    visible_list = [True] * len(df_data.columns)

    button_list.append(dict(label="All",
                            method="update",
                            args=[{"visible": visible_list},
                                  {"showlegend": True}]))
    # print(button_list)
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=button_list,active=0)])

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 20

    fig.update_xaxes(title_font_color='white', tickfont_color='white', gridcolor='grey')
    fig.update_yaxes(title_font_color='white', tickfont_color='white', gridcolor='grey')
    fig.update_layout(title_font_color='white', legend_font_color='white', paper_bgcolor='black', plot_bgcolor='black',title_font_size=25)
    fig.update_annotations(font_color='white',font_size=14)
    
    ygraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return ygraphJSON
    # fig.show()

def gauge_plot(borough_name,val_date='2018-01-07'):

    # Fetch data for input date and borough
    df_air = pd.read_csv('data_mean/data_borough/Daily_{}.csv'.format(borough_name))
    df_air['date'] = df_air.MeasurementDateGMT
    df_air = df_air.drop(['MeasurementDateGMT'], axis=1)
    df_air_value = df_air.query('date == @val_date')
    df_air_value = df_air_value.rename(columns={' Nitric Oxide (ug/m3)': 'NO',' Nitrogen Dioxide (ug/m3)': 'NO2',
                                            ' Oxides of Nitrogen (ug/m3)':'NOX',' Ozone (ug/m3)': 'O3',
                                            ' PM10 Particulate (ug/m3)': 'PM10',' PM2.5 Particulate (ug/m3)': 'PM25',
                                            ' Sulphur Dioxide (ug/m3)': 'SO2',' Carbon Monoxide (mg/m3)': 'CO'})

    fig = make_subplots(rows=1, cols=2)

    color_dict = {'NO': '#EF9A9A', 'NO2': '#CE93D8', 'NOX': '#90CAF9',
                  'O3': '#A5D6A7', 'PM10': '#E6EE9C',
                  'PM25': '#BCAAA4', 'SO2': '#ff944d', 'CO': '#4d4d33'}
    max_val = df_air_value.max(axis=1).values[0]
    i = 0
    for col in df_air_value.columns:
        if col == 'date':
            continue
        print(df_air_value[col].values[0])
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=df_air_value[col].values[0],
                domain={'row': 0, 'column': i},
                title={'text': col},
                gauge={'axis': {'range': [None, max_val], 'visible': False},
                       'bar': {'color': color_dict.get(col)}}))

        i = i + 1

    fig.update_layout(grid={'rows': 1, 'columns': i, 'pattern': "independent"})
    fig.update_layout(height=200,margin=dict(
        l=10,
        r=10,
        b=10,
        t=10,
        pad=4
    ))
    fig.update_layout(title_font_color='white', legend_font_color='white', paper_bgcolor='black', plot_bgcolor='black')
    fig.update_traces(gauge_bordercolor='black',selector=dict(type='indicator'))
    fig.update_traces(title_font_color='white',number_font_color='white')
    gaugeJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return gaugeJSON


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

#@app.route('/london')
#def london():
#    return render_template('london.html')

@app.route('/boroughwise')
def region():
    return render_template('boroughwise.html')

val_date='2018-01-07'
@app.route('/borough', methods=['GET', 'POST'])
def borough():
 if request.method == 'POST' :
    borough = request.form.get('borough')
    #val_date = request.form.get('date')
    graph_borough = plot_line_air_pollutant(borough)
    min_air = fetch_min_air_pollutant(borough)
    gauge = gauge_plot(borough)

 else :
    borough = request.form.get('borough')
    #borough = 'Camden'
    val_date = request.form.get('date')
    graph_borough = plot_line_air_pollutant(borough)
    min_air = fetch_min_air_pollutant(borough)
    gauge = gauge_plot(borough,val_date)

 return render_template('borough.html', borough=borough,graph=graph_borough,
                           min_air_pollutant=min_air,gauge=gauge)

if __name__ == '__main__':
    app.run(debug=True)
