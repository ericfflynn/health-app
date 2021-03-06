from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import plotly.express as px
import numpy as np
import requests

#Data Pull
Response = requests.get('https://ericfflynn.github.io/Data/HealthAutoExport.json')
data = Response.json()

df = pd.DataFrame(data['data']['workouts'])
df.drop(['humidity','stepCadence','swimCadence','stepCount','totalSwimmingStrokeCount', \
       'heartRateRecovery', 'isIndoor', 'temperature', 'flightsClimbed','speed'],axis=1,inplace=True)
    
df['Start'] = pd.to_datetime(df['start']).apply(lambda x: x.date())
df['End'] = pd.to_datetime(df['end']).apply(lambda x: x.date())
df['Startstr'] = df['Start'].apply(lambda x: x.strftime('%Y-%m-%d'))
df['start'] = df['start'].apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S %z"))
df['end'] = df['end'].apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S %z"))
df['Duration'] = df['end']-df['start']
df['YearMonth'] = df['Start'].apply(lambda x: x.strftime("%m-%Y"))
df['YearWeek'] = df['start'].apply(lambda x: x.strftime("%Y-%W"))
for i in ['activeEnergy','avgHeartRate','maxHeartRate','distance','totalEnergy','intensity',]:
    df[i] = df[i].apply(lambda x: x['qty'])
    
Workout_stats = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Date"),
                    html.Div(id='Date'
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Type"),
                    html.P(id='Type',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Duration"),
                    html.Div(id='Duration',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Active Cal"),
                    html.Div(id='Active_cal',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Avg HR"),
                    html.P(id='Avg_hr',
                    ),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Max HR"),
                    html.P(id='Max_hr',
                    ),
                ]
            )
        ),
    ],style={'textAlign':'center'}
)

slicers = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H4("Select Workout Date:",style={'textAlign': 'center'})
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Dropdown(list(df['Startstr']), df['Startstr'].iloc[0],id='dropdown')
                ]
            )
        )
    ]
)
        


Latest_Update = 'Latest Update: '+ df['Start'].iloc[0].strftime("%m/%d/%Y")

external_stylesheets = [dbc.themes.BOOTSTRAP]


app = Dash(__name__, external_stylesheets = external_stylesheets)

server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Eric Flynn's Personal Fitness Dashboard",className='header-title'
                ),
                 html.P(
                     children=Latest_Update, className='header-description',
                ),
            ],
            className='header',
        ),
          
        
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Workout Type", className="menu-title"),
                    dcc.Dropdown(
                        id="type-filter",
                        options=[
                            {"label": workout_type, "value": workout_type}
                            for workout_type in df.name.unique()
                        ],
                        value="Traditional Strength Training",
                        clearable=False,
                        searchable=False,
                        className="dropdown",
                    ),
                ],
            ),
            html.Div(
                children=[
                    html.Div(
                        children="Date Range",
                        className="menu-title"
                        ),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=df.Start.min(),
                        max_date_allowed=df.Start.max(),
                        start_date=df.Start.min(),
                        end_date=df.Start.max(),
                    ),
                ]
            ),
        ],
        className="menu",
    ),
        dcc.Graph(
            id='figb',className='wrapper'),
        
        dbc.Card(slicers),
        
        dbc.Card(Workout_stats),
        
        dcc.Graph(id='graph'),

    ]
)

@app.callback(
        Output("figb", "figure"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"))


def Update_Bar_Chart(workout_type, start_date, end_date):
    sdate = datetime.strptime(start_date,"%Y-%m-%d").date()
    edate = datetime.strptime(end_date,"%Y-%m-%d").date()
    mask = (
        (df.name == workout_type)
        & (df.Start >= sdate)
        & (df.Start <= edate)
    )
    filtered_df = df.loc[mask, :]
    dim = pd.DataFrame(pd.date_range(sdate,edate-timedelta(days=1),freq='d')) 
    dim['YearMonth'] = dim[0].apply(lambda x: x.strftime("%m-%Y"))
    Dim_month = pd.DataFrame(list(np.unique(dim['YearMonth'])),columns=['Month'])
    Grouped = filtered_df.groupby(['YearMonth']).agg({'name':'count','activeEnergy':'sum','maxHeartRate':'max'}). \
    reset_index().rename(columns={'name':'# Workouts','activeEnergy':'Active Cal','maxHeartRate':'Max HR','YearMonth':'Month'})
    Monthly =  Dim_month.merge(Grouped,on='Month',how='left')
    Monthly['Date'] = Monthly['Month'].apply(lambda x: datetime.strptime(x,"%m-%Y").date())
    Monthly = Monthly.sort_values(by = ['Date'])
    #Monthly.drop('Date', axis = 1, inplace=True)
    Monthly = Monthly.reset_index(drop=True)
    Monthly['Avg Cal'] = Monthly['Active Cal'] / Monthly['# Workouts']
    Monthly.fillna(0,inplace=True)
  
    figb = px.bar(Monthly[-12:], x='Month', y='# Workouts',text_auto=True)
    figb.update_layout(
        yaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
        xaxis={'visible': True, 'showticklabels': True, 'title':None,'showgrid':False},
        title={'text':'Workouts Per Month','x':0.5,'y':0.9,'xanchor':'center','yanchor':'top'}
                      )
    figb.update_traces(marker_color='#079A82')
    return figb


@app.callback(
    Output('Date', 'children'),
    Output('Duration', 'children'),
    Output('Active_cal', 'children'),
    Output('Avg_hr', 'children'),
    Output('Max_hr', 'children'),
    Output('Type', 'children'),
    Input('dropdown', 'value'))

def update_workout_stats(date):
    Day_data = df.loc[df['Startstr'] == date].reset_index()
    Date = Day_data['Start'].iloc[0].strftime("%Y-%m-%d")
    Duration = str(Day_data['end'][0] - Day_data['start'][0])
    Active_cal = "{:,.0f}".format(Day_data['activeEnergy'][0])
    Avg_hr = "{:,.0f}".format(Day_data['avgHeartRate'][0])
    Max_hr = "{:,.0f}".format(Day_data['maxHeartRate'][0])
    Type = Day_data['name'][0]
    return Date, Duration, Active_cal, Avg_hr, Max_hr, Type


@app.callback(
    Output('graph', 'figure'),
    Input('dropdown', 'value'))

def update_figure(date):
    Day_data = df.loc[df['Startstr'] == date].reset_index()
    Heart_Rate = pd.DataFrame.from_dict(Day_data['heartRateData'][0])
    fig = px.line(x=Heart_Rate['date'],y=Heart_Rate['qty'])
    fig.update_layout(yaxis={'visible':True, 'title':'BPM'},
                      xaxis={'visible':False})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
