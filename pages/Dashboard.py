import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px
import os 
import altair as alt
import pymysql
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import json

st.set_page_config(
    page_title="Fitness Dashboard: Eric Flynn",
    layout="wide",
    initial_sidebar_state="expanded",  
)

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
key = os.environ.get('KEY')
headers = {"x-api-key":key}

def sql_connect():
	global conn
	conn = pymysql.connect(
	host=os.environ.get('HOST'),
    user=os.environ.get('USER'),
    password=os.environ.get('DBPW'),
    db=os.environ.get('DB')
	)
	cursor = conn.cursor()




# @st.cache(ttl=21600)
# def get_data():
# 	result = requests.get('https://wz52lc2sa0.execute-api.us-east-2.amazonaws.com/includeget/workouts',headers=headers)
# 	data = result.json()
# 	df = pd.read_json(data)
# 	for i in ['start','end']:
# 		df[i+'_dt'] = df[i].apply(lambda x: datetime.datetime.strptime(x[:-5],"%Y-%m-%dT%H:%M:%S"))
# 		df[i] = df[i].apply(lambda x: x[0:10])
# 	df['Duration'] = df['end_dt'] - df['start_dt']
# 	df['Duration'] = df['Duration'].apply(lambda x: str(x)[-8:])
# 	df.sort_values(by=['start'], ascending=False, inplace=True)
# 	df.reset_index(inplace=True, drop=True)
# 	df.rename(columns={'name':'Workout Type','start':'Date','activeEnergy.qty':'Calories','avgHeartRate.qty':'Avg BPM','maxHeartRate.qty':'Max BPM'},inplace=True)
# 	for i in ['Calories','Avg BPM']:
# 		df[i] = df[i].apply(lambda x: int(x))
# 	df['Month'] = df['start_dt'].apply(lambda x: x.strftime("%Y-%m"))
# 	def f(row):
# 		if row['Workout Type'] in ['Traditional Strength Training', 'Functional Strength Training'] :
# 			val = 'Strength Training'
# 		elif row['Workout Type'] in ['Tennis','Golf']:
# 			val = 'Sport'
# 		else:
# 			val = 'Cardio/Core'
# 		return val
# 	df['Category'] = df.apply(f,axis=1)
# 	return df

@st.cache(ttl=21600)
def get_data():
	sql_connect()
	query = "SELECT name, start, end, `activeEnergy.qty`, `avgHeartRate.qty`, `maxHeartRate.qty`, heartRateData, BodyPart FROM Workouts WHERE start >= '2022-01-01'"
	df = pd.read_sql(query, conn)
	for i in ['start','end']:
		df[i+'_dt'] = df[i].apply(lambda x: x.to_pydatetime())
		df[i] = df[i].apply(lambda x: x.strftime("%Y-%m-%d"))
	df['Duration'] = df['end_dt'] - df['start_dt']
	df['Duration'] = df['Duration'].apply(lambda x: str(x)[-8:])
	df.sort_values(by=['start'], ascending=False, inplace=True)
	df.reset_index(inplace=True, drop=True)
	df.rename(columns={'name':'Workout Type','start':'Date','activeEnergy.qty':'Calories','avgHeartRate.qty':'Avg BPM','maxHeartRate.qty':'Max BPM', 'BodyPart':'Body Part'},inplace=True)
	for i in ['Calories','Avg BPM']:
		df[i] = df[i].apply(lambda x: int(x))
	df['Month'] = df['start_dt'].apply(lambda x: x.strftime("%Y-%m"))
	def f(row):
		if row['Workout Type'] in ['Traditional Strength Training', 'Functional Strength Training'] :
			val = 'Strength Training'
		elif row['Workout Type'] in ['Tennis','Golf']:
			val = 'Sport'
		else:
			val = 'Cardio/Core'
		return val
	df['Category'] = df.apply(f,axis=1)
	conn.close()
	return df

df = get_data()


st.title("Dashboard")	

st.markdown("This page is the dashboard itself. Please play around with the slicers on the left hand side to modify the date range and workout type.")
st.write('***')
types = pd.concat([pd.Series(['Select All']), df['Workout Type'].drop_duplicates()])
types_choice = st.sidebar.selectbox('Workout Type',types)
start_date = st.sidebar.date_input('Start Date',min(df['start_dt']).to_pydatetime())
end_date = st.sidebar.date_input('End Date',datetime.datetime.today())

if types_choice == 'Select All':
	dfdis = df.query("start_dt >= @start_date & end_dt <= @end_date")
else:
	dfdis = df.query("start_dt >= @start_date & end_dt <= @end_date & `Workout Type` == @types_choice")	

totalworkouts = len(dfdis)
maxhr = dfdis['Max BPM'].max()
avgcalories = dfdis['Calories'].mean()
avghr = dfdis['Avg BPM'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
	st.metric(label='Total Workouts', value = int(totalworkouts))
with col2:
	st.metric(label='Max BPM', value = int(maxhr))
with col3:
	st.metric(label='Avg Calories', value = int(avgcalories))
with col4:
	st.metric(label='Avg BPM', value = int(avghr))

altbar = alt.Chart(dfdis).mark_bar().encode(
	x='Month:T',
	y=alt.Y(field='Workout Type',aggregate='count',type='quantitative', title='# Workouts')
	)

st.altair_chart(altbar, use_container_width=True)
#st.write(dfdis[['Category','Workout Type','Date','Duration','Calories','Avg BPM','Max BPM']],use_container_width=True)

st.header("Single Workout Analysis")
st.write('***')
dfgrid = dfdis[['Workout Type', 'Date']]
gd = GridOptionsBuilder.from_dataframe(dfgrid)
gd.configure_pagination(enabled=True, paginationAutoPageSize=False,paginationPageSize=10)
gd.configure_selection(selection_mode='single',use_checkbox=True)
gridoptions = gd.build()
grid_table = AgGrid(dfgrid, fit_columns_on_grid_load=True, gridOptions=gridoptions,columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

try:
	row = grid_table["selected_rows"][0]
	ind = row['_selectedRowNodeInfo']['nodeRowIndex']
	dfshow = dfdis[['Category','Workout Type','Body Part','Date','Duration','Calories','Avg BPM','Max BPM']].loc[ind]
	st.table(dfshow)
	# hrdata = dfdis['heartRateData'][ind]
	hrdata = pd.DataFrame(json.loads(dfdis['heartRateData'][ind]))
	hrdata['date'] = hrdata['date'].apply(lambda x: datetime.datetime.strptime(x[0:18],"%Y-%m-%d %H:%M:%S"))
	#st.write(hrdata)
	source = hrdata
	bottom = min(hrdata['qty'])
	top = max(hrdata['qty'])
	line = alt.Chart(source).mark_line().encode(
	    x='date:T',
	    y=alt.Y(field='qty', type='quantitative', aggregate='max',title="BPM", scale=alt.Scale(domainMin=bottom,domainMax=top))
	    )
	st.altair_chart(line, use_container_width=True)

except:
 	st.error("Select a workout to see more details!")






