import streamlit as st

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

st.title("Personal Fitness Dashboard")
st.write('***')

st.subheader("About")

st.markdown("Thank you for checking out my personal fitness dashboard! This website serves a central location for me to track statistics regarding my workout history. I have also added features to be able to add \
            additional functionality including tagging the body part targeted for a given strenth training session.")

st.subheader("Goals")

st.markdown("- Create a fully automated, cloud based ETL pipeline")
st.markdown("- Enable CRUD operations to tag/maintain workout history database")
st.markdown("- Visualize workout history summary statistics")

st.markdown('''
<style>
[data-testid="stMarkdownContainer"] ul{
    padding-left:40px;
}
</style>
''', unsafe_allow_html=True)

st.subheader("Data Pipeline")

st.markdown("All of the data included on this dashboard was first collected using an Apple Watch.  \
            The data is then sent to a REST API via the HealthAutoExport iPhone application. Next, it is processed by an AWS Lambda function and loaded into a MySQL \
            database where it is stored. This leads to a fully automated, cloud based pipeline. For a detailed explanation please check out my Medium article \
            [here](https://medium.com/@ericfflynn/a-cloud-based-etl-pipeline-apple-health-data-to-mysql-48391576ce8e).")