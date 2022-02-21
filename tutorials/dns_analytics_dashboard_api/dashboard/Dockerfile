FROM python:3

ADD ./app.py /

RUN pip install streamlit
RUN pip install pandas
RUN pip install requests
RUN pip install altair

EXPOSE 8502

CMD ["streamlit","run","app.py","--server.port", "8502"]