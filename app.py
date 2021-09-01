'''
Module : Final Year Project
Topic : Impact of Covid-19 on London Air Quality
Description : Create a web based application to showcase the impact of Covid-19 restrictions on London air quality. 
              Period of Analysis - 1st Jan, 2018 to 30th Jun, 2021
References: 
https://community.plotly.com/t/changing-the-background-colour-of-a-graph/29246
https://plotly.com/python/reference/indicator/
https://towardsdatascience.com/lets-make-a-map-using-geopandas-pandas-and-matplotlib-to-make-a-chloropleth-map-dddc31c1983d
https://plotly.com/python/reference/layout
https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946
'''

import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
import plotly
import json
from flask import Flask, render_template, request
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# creates the WSGI application
app = Flask(__name__)

# This function receives the borough name as input. It then fetches the date
# when each air pollutant had the least emission and outputs a dataframe
# containing the air pollutant name, date and the corresponding minimum value of air
# pollutant
def fetch_min_air_pollutant(borough_name):
    air_data = pd.read_csv('data_mean/data_borough/Daily_{}.csv'.format(
              borough_name))
    air_data['date'] = air_data.MeasurementDateGMT
    air_data.index = pd.to_datetime(air_data.date)
    air_data = air_data.drop(['MeasurementDateGMT'], axis=1)

    col_list = ['AirPollutant', 'Date', 'Value']
    df_min_air = pd.DataFrame(columns=col_list)

    for col in air_data:
        if col == 'date':
            continue
        data = air_data.loc[[air_data.loc[air_data[col] > 0, col].idxmin()]]
        air_date = pd.to_datetime(data.date).dt.date
        val = data[col].values[0]
        val = round(val, 2)
        data_list = [col, air_date[0], val]
        df = pd.DataFrame([data_list], columns=col_list)
        df_min_air = df_min_air.append(df)
    return df_min_air.to_html(index=False)

# This function receives the borough name as input and outputs a multi-line
# chart to showcase the weekly trent of each air pollutant in a plotly
# interactive chart
def plot_line_air_pollutant(borough_name):
    air_data = pd.read_csv('data_mean/data_borough/{}.csv'.format(borough_name))
    air_data['date'] = air_data.MeasurementDateGMT
    air_data = air_data.drop(['MeasurementDateGMT'], axis=1)
    if borough_name == 'Wandsworth':
        air_data['date'] = pd.to_datetime(air_data['date'], format='%d/%m/%Y')
        air_data['date'] = air_data['date'].dt.strftime('%Y-%m-%d')
    # df_data['date'] = df_data.index
    df_data_wo_date = air_data.drop(['date'], axis=1)
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

    # Add traces to the plot
    init = 1

    color_dict = {'NO': '#EF9A9A', 'NO2': '#CE93D8', 'NOX': '#90CAF9',
                  'O3': '#A5D6A7', 'PM10': '#E6EE9C',
                  'PM25': '#BCAAA4', 'SO2': '#ff944d', 'CO': '#4d4d33'}

    i = 0
    for col in air_data.columns:
        if col == 'date':
            continue
        i = i + 1
        fig.add_trace(
            go.Scatter(x=air_data.date[:init],
                       y=air_data[col][:init],
                       name=col,
                       visible=True,
                       line=dict(color=color_dict.get(col))))

    # Animation
    frame_list = []

    for k in range(init, len(air_data) + 1):

        animation_list = []
        for col in air_data.columns:
            animation_list.append(
                go.Scatter(x=air_data.date[:k], y=air_data[col][:k]))
        frame_list.append(go.Frame(data=animation_list))

    fig.update(frames=frame_list)

    # Extra Formatting to update the lockdown period and ULEZ(where applicable)
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='white',
                     ticklen=10,mirror=True,showline=True)
    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=1,mirror=True,showline=True)
    fig.update_layout(yaxis_tickformat=',')
    fig.update_layout(legend=dict(x=0, y=1.12), legend_orientation="h")
    if borough_name in ['Camden','Islington', 'Kensington and Chelsea',
                        'Lambeth','Southwark','Westminster','City of London']:
        fig.add_vline(x='2019-04-08')
        fig.add_annotation(x='2019-03-28',
                           text="Start of ULEZ (8th April, 2019)",
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

    # Create buttons for user interaction
    button_list = []
    button_list.append(dict(label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 1000},"transition": {"duration": 0}}]))

    visible_list = [False] * (len(air_data.columns) - 1)
    i = 0

    for col in air_data.columns:
        if col == 'date':
            continue
        visible_list[i] = True
        button_list.append(dict(label=col,
                                method="update",
                                args=[{"visible": visible_list[:]},
                                      {"showlegend": True}]))

        visible_list[i] = False
        i = i + 1

    visible_list = [True] * len(air_data.columns)

    button_list.append(dict(label="All",
                            method="update",
                            args=[{"visible": visible_list},
                                  {"showlegend": True}]))
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=button_list,active=0)])

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 20

    # Update axes for the line charts
    fig.update_xaxes(title_font_color='white', tickfont_color='white', gridcolor='grey')
    fig.update_yaxes(title_font_color='white', tickfont_color='white', gridcolor='grey')
    fig.update_layout(title_font_color='white', legend_font_color='white', paper_bgcolor='black', plot_bgcolor='black',title_font_size=25)
    fig.update_annotations(font_color='white',font_size=14)

    # Return graph template in required format to render the graph object on
    # HTML
    timegraph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return timegraph

# This function receives the borough name and a date (01-01-2018 -
# 30-06-2021) and outputs the raw value of each pollutant in the borough on
# that specific date in a gauge/speedometer chart
def gauge_plot(borough_name,val_date='2021-06-30'):

    # Fetch data for input date and borough
    df_air = pd.read_csv('data_mean/data_borough/Daily_{}.csv'.format(borough_name))
    df_air['date'] = df_air.MeasurementDateGMT
    if borough_name == 'Wandsworth':
        df_air['date'] = pd.to_datetime(df_air['date'],format='%d/%m/%Y')
        df_air['date'] = df_air['date'].dt.strftime('%Y-%m-%d')
    df_air['date'] = pd.to_datetime(df_air['date'])
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
        l=9.8,
        r=9.8,
        b=9.8,
        t=9.8,
        pad=4
    ))
    fig.update_layout(title_font_color='white', legend_font_color='white', paper_bgcolor='black', plot_bgcolor='black')
    fig.update_traces(gauge_bordercolor='black',selector=dict(type='indicator'))
    fig.update_traces(title_font_color='white',number_font_color='white')
    gaugeJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return gaugeJSON


# Decorator for home page
@app.route('/')
def home():
    return render_template('home.html')

# Decorator for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Decorator for boroughwise page
@app.route('/boroughwise')
def region():
    return render_template('boroughwise.html')

# Decorator for borough page
@app.route('/borough', methods=['GET', 'POST'])
def borough():
 if request.method == 'POST' :
    borough = request.form.get('borough')
    val_date = '2021-06-30'
    graph_borough = plot_line_air_pollutant(borough)
    min_air = fetch_min_air_pollutant(borough)
    gauge = gauge_plot(borough)
 else :
    borough = request.values.get('borough')
    val_date = request.values.get('val_date')
    graph_borough = plot_line_air_pollutant(borough)
    min_air = fetch_min_air_pollutant(borough)
    gauge = gauge_plot(borough,val_date)

 return render_template('borough.html', borough=borough,graph=graph_borough,
                           min_air_pollutant=min_air,gauge=gauge,
                           display_date=val_date)


if __name__ == '__main__':
    app.run()
