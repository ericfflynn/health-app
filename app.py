import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px
import os 

st.set_page_config(
    page_title="Fitness Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
key = os.environ.get('key')
headers = {"x-api-key":key}

@st.cache
def get_data():
	result = requests.get('https://wz52lc2sa0.execute-api.us-east-2.amazonaws.com/includeget/workouts',headers=headers)
	data = result.json()
	df = pd.DataFrame.from_records(data)
	for i in ['start','end']:
		df[i+'_dt'] = df[i].apply(lambda x: datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
		df[i] = df[i].apply(lambda x: x[0:10])
	df['Duration'] = df['end_dt'] - df['start_dt']
	df['Duration'] = df['Duration'].apply(lambda x: str(x)[-8:])
	df.sort_values(by=['start'], ascending=False, inplace=True)
	df.reset_index(inplace=True, drop=True)
	df.rename(columns={'name':'Workout Type','start':'Date','activeEnergy':'Calories','avgHR':"Avg BPM"},inplace=True)
	for i in ['Calories','Avg BPM']:
		df[i] = df[i].apply(lambda x: int(x))
	df['Month'] = df['start_dt'].apply(lambda x: x.strftime("%Y-%m"))
	return df

df = get_data()

st.title("Personal Fitness Dashboard")
st.markdown("#")
types = pd.concat([pd.Series(['Select All']), df['Workout Type'].drop_duplicates()])
types_choice = st.sidebar.selectbox('Workout Type',types)
start_date = st.sidebar.date_input('First Date',min(df['start_dt']).to_pydatetime())
end_date = st.sidebar.date_input('Last Date',max(df['end_dt']).to_pydatetime())

config = {'displayModeBar': False}

if types_choice == 'Select All':
	dfdis = df.query("start_dt >= @start_date & end_dt <= @end_date")
	totalworkouts = len(dfdis)
	maxhr = dfdis['maxHR'].max()
	avgcalories = dfdis['Calories'].mean()
	avghr = dfdis['Avg BPM'].mean()
	dfbar = dfdis.groupby(['Month']).agg({'Workout Type':'count'}).rename(columns={'Workout Type':'# Workouts'})
	bar_chart = px.bar(dfbar, x= dfbar.index, y='# Workouts')
	col1_1, col2_1, col3_1, col4_1 = st.columns(4)
	with col1_1:
		st.metric(label='Total Workouts', value = int(totalworkouts))
	with col2_1:
		st.metric(label='Max BPM', value = maxhr)
	with col3_1:
		st.metric(label='Avg Calories', value = int(avgcalories))
	with col4_1:
		st.metric(label='Avg BPM', value = int(avghr))
	st.markdown("#")
	col1_2, col2_2 = st.columns(2)
	with col1_2:
		st.plotly_chart(bar_chart, config=config)
	with col2_2:
		st.dataframe(dfdis[['Workout Type','Date','Duration','Avg BPM','Calories']])
else:
	dfdis = df.query("start_dt >= @start_date & end_dt <= @end_date & `Workout Type` == @types_choice")
	totalworkouts = len(dfdis)
	maxhr = dfdis['maxHR'].max()
	avgcalories = dfdis['Calories'].mean()
	avghr = dfdis['Avg BPM'].mean()
	dfbar = dfdis.groupby(['Month']).agg({'Workout Type':'count'}).rename(columns={'Workout Type':'# Workouts'})
	bar_chart = px.bar(dfbar, x= dfbar.index, y='# Workouts')
	col1_1, col2_1, col3_1, col4_1 = st.columns(4)
	with col1_1:
		st.metric(label='Total Workouts', value = int(totalworkouts))
	with col2_1:
		st.metric(label='Max BPM', value = maxhr)
	with col3_1:
		st.metric(label='Avg Calories', value = int(avgcalories))
	with col4_1:
		st.metric(label='Avg BPM', value = int(avghr))
	st.markdown("#")
	col1_2, col2_2 = st.columns(2)
	with col1_2:
		st.plotly_chart(bar_chart, config=config)
	with col2_2:
		st.dataframe(dfdis[['Workout Type','Date','Duration','Avg BPM','Calories']])

