import streamlit as st
from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder
import pandas as pd
import pymysql
import os
st.title("Data Update")
st.markdown("The purpose of this page is to enable the me to maintain the underlying database and either delete/update information. \
			Since there is no built in functionality within Apple's Health app to tag the body part trained, I can use this page to \
			update additional information about a given workout.")

with st.form("Login"):
	Access = st.text_input("Please Enter Password")
	st.form_submit_button("Login")

if Access == os.environ.get('PASSWORD'):
	st.write("Welcome Eric!")
	conn = pymysql.connect(
		host=os.environ.get('HOST'),
	    user=os.environ.get('USER'),
	    password=os.environ.get('DBPW'),
	    db=os.environ.get('DB')
		)
	cursor = conn.cursor()


	def StoreData():
		query="SELECT name, start, end, BodyPart FROM Workouts WHERE name like 'Traditional Strength Training' ORDER BY start DESC"
		tdf = pd.read_sql(query, conn)
		return tdf
	tdf = StoreData()

	gd = GridOptionsBuilder.from_dataframe(tdf)
	gd.configure_pagination(enabled=True, paginationAutoPageSize=False,paginationPageSize=10)
	gd.configure_selection(selection_mode='single',use_checkbox=True)
	gridoptions = gd.build()
	grid_table = AgGrid(tdf, gridOptions=gridoptions)

	try:
		row = grid_table["selected_rows"][0]
		st.write(row)
		start = row['start']
		start = start.replace("T", " ")
	except:
		st.write("Please Select a row")

	def UpdateBodyPart(start):
		try:
			cursor.execute("UPDATE Workouts set BodyPart = %s WHERE start = %s",(Part,start))
			conn.commit()
			st.success("Row Updated")
		except:
			st.error("Invalid Query")

	with st.form("Update Body Part", clear_on_submit=True):
		Part = st.text_input("Body Part")
		if st.form_submit_button("Update"):
			try:
				UpdateBodyPart(start)
			except:
				st.error("Make Sure to select a workout")



	def DelWorkout(start):
		cursor.execute("DELETE FROM Workouts WHERE start = %s",(start))
		conn.commit()
		st.success("Row Deleted")

	with st.form("Delete Workout", clear_on_submit=True):
		if st.form_submit_button("Delete"):
			try:
				DelWorkout(start)
			except:
				st.error("Make Sure to select a workout")




