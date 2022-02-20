FROM python:3

ADD ./apiserver.py /

RUN pip install pandas
RUN pip install fastapi
RUN pip install uvicorn[standard]

EXPOSE 7000

CMD ["uvicorn","apiserver:app","--host","0.0.0.0","--port","7000"]

