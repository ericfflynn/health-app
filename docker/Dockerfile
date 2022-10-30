FROM python:3.10
EXPOSE 8501
COPY ./assets ./app
WORKDIR ./app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["streamlit",  "run", "app.py"]
