## Containerized Dashboard and API

In this post we are examining how to deploy a containerized dashboard with a custom API that is also containerized. In future posts we may add additional components and capability. The dashboard and api will not be overly complex, the focus is more to discuss data flow and containerizing data science microservices.

Assumptions: The post assumes some degree of understanding with containers. In our case we are using Docker. More on Docker can be found at https://www.docker.com/resources/what-container. If you don’t you can download Docker and just copy the repo from Github.

Tech Stack:

The current stack will be as follows:

Docker

Streamlit (Dashboard)

FastAPI

GitHub Files
All files and data for this post can be found here:

cooingbicycle88/substack/tutorials/dns_analytics_dashboard_api

Data
In my previous post we discussed how to run DNS analytics using the pandas library. In this post we will use the same dataset for continuity.

Access Data

The data is currently in and open github repository, so we can access this data via pandas by simply reading the raw data url. To access this data you can use the following code:

import pandas as pd

csv = "https://raw.githubusercontent.com/cooingbicycle88/substack/main/tutorials/logs.csv"

import pandas as pd

df = pd.read_csv(csv,index_col=0)

df.show()
We will use this code snippet in our API

Network Diagram
Below is our simple architecture for our current stack.


Fast API
FastAPI is a great framework for building API’s and creating documentation, without dealing with a lot of the headaches that come with building custom API’s. It also comes with a deployed Swagger UI Interface at runtime, eliminating the need for creating this separately.

API Script
We are going to containerize the API, but we still want to locally test, so you will need to install fastAPI. It is a simple install. See documentation on how to do this here: fastAPI install

I am not going to run through line by line of code, but to get the API up locally you will simply need to run the following script.

Note: You do not have to locally test. You can simply skip to the end download the repo and run the docker-compose file if docker and docker compose are already installed.

from fastapi import FastAPI

import pandas as pd

from pydantic import BaseModel

description = """
Substack API -
Connects to DNS Data
"""

tags_metadata = [
    {
        "name": "alldata",
        "description": "Get all Data",
    },
     {
        "name": "uniqueip",
        "description": "get unique ips",
    },
     {
        "name": "data",
        "description": "get subsets of data",
    },
    
]

class IP(BaseModel):
    ip : str

csv = "https://raw.githubusercontent.com/cooingbicycle88/substack/main/tutorials/logs.csv"
df = pd.read_csv(csv,index_col=0)


app = FastAPI(title="Substack Analytics API",
    description=description,openapi_tags=tags_metadata)


@app.get('/alldata',tags=['alldata'])
def alldata():
    return df.to_json()

@app.get('/uniqueip',tags=['uniqueip'])
def uniqe_ips():
    uniques = list(df['IP'].unique())
    return {"uniqueips":uniques}

@app.get('/data/{numbytes}',tags=['data'])
def subset_by_bytes(numbytes:int):
    subset = df[df['Bytes'] > numbytes]
    subset.index = range(0,len(subset))
    return subset.to_json()

@app.post('/data/ip',tags=['data'])
def subset_by_ip(ipclass: IP):
    subset = df[df['IP'] == ipclass.ip]
    subset.index = range(0,len(subset))
    return subset.to_json()
Assuming you’ve saved the file as

apiserver.py
You will need to go to the directory you saved the file to and run the following command:

uvicorn apiserver:app --host 7000
The host option can be any port of your choosing, I’ve simply chosen this port. Upon run open a browser and go to:

localhost:7000/docs
You should see the following:


You can test that the API is running fine and then move on to containerizing the API.

Docker Container - API

There are a few requirements for the API to run in a Docker environment.

Must have python installed

Must have necessary packages

Must have command than runs the dashboard

Must have the port exposed

Now that the requirements have been listed we can created our Dockerfile. In the following section we assume that you have all of these files in the same directory.

Python Image - Has python already installed

FROM python:3
Add scripts

ADD ./apiserver.py /  
Install packages

In most cases we use a requirments.txt file and simply add all package names to it then run a command like a pip install -r requirments.txt command. In this case since we only need three libraries we won’t bother to build that out.

RUN pip install pandas
RUN pip install fastapi
RUN pip install uvicorn[standard]
Expose Port

Here we expose port 7000 so that we can connect the dashboard to the API.

EXPOSE 7000
Run the API

CMD ["uvicorn","apiserver:app","--host","0.0.0.0","--port","7000"]
Full Docker Script:

FROM python:3

ADD ./apiserver.py /

RUN pip install pandas
RUN pip install fastapi
RUN pip install uvicorn[standard]

EXPOSE 7000

CMD ["uvicorn","apiserver:app","--host","0.0.0.0","--port","7000"]
Streamlit
Streamlit is a newer dashboard framework. It is particularly useful for building prototype applications and development applications. More on this framework can be found here Streamlit - Getting Started.

If you are wanting to test locally you can do so by installing streamlit, which can be found in their documentation in the link provided above. However, we will skip that and run through the scripts and Dockerfile.

Dashboard Script

The dashboard script is a simple script that submits requests to our api, received the data from the api, then provides some visualizations. This is a very minimalistic dashboard.

Code

import streamlit as st

import os

import requests

import pandas as pd
import json
import altair as alt


API_HOST = os.environ.get("API_HOST","http://localhost:7000")

st.set_page_config(layout="wide")
st.info("Click arrow button to left to see sidebar")
st.title("Substack - DNS Analytics\n")
with st.sidebar:
    st.title("DNS - Analytics Container")
    expander1 = st.expander("Substack Analytics Dashboard Container")
    expander1.write("This container runs analytics and connects to the api dashboard")
    expander2 = st.expander("Code")
    expander2.write("You are welcome to reuse any code or modify as necessary")
    expander3 = st.expander("Environment Variables")
    expander3.write(f"API_HOST environment variable current set to {API_HOST}")


col1, col2 = st.columns((1,6))


col2.subheader("All Data")
df = pd.read_json(requests.get(f"{API_HOST}/alldata").json())
col2.dataframe(df)


col1.subheader("Unique IP")
uniques = pd.DataFrame(requests.get(f"{API_HOST}/uniqueip").json())
col1.dataframe(uniques)

st.subheader("Visualizations")

flter = st.selectbox("Select Filter", ['By IP', 'By Bytes'])
if flter == "By Bytes":
    bts = st.slider("Subset Data By Bytes Greater Than:",10000,1000000,step=25000)
    col1A, col2B = st.columns((2,2))
    subset_bytes = pd.read_json(requests.get(f"{API_HOST}/data/{bts}").json())
    col1A.markdown(f"##### Number of Records: {len(subset_bytes)}")
    col1A.dataframe(subset_bytes)
    col2B.write("")
    bars = alt.Chart(subset_bytes,title="Byte Distribution",height=350).mark_bar().encode(
                    x='Bytes',
                    y="count()",tooltip=["Bytes"]
                )
    col2B.altair_chart(bars,use_container_width=True)
else:
    ip = st.selectbox("IP",uniques['uniqueips'].values)
    col1A, col2B = st.columns((2,2))
    print(requests.post(f"{API_HOST}/data/ip",data={'ip': ip}).json())
    subset_ip = pd.read_json(requests.post(f"{API_HOST}/data/ip",data=json.dumps({'ip': ip})).json())
    col1A.markdown(f"##### Number of Records: {len(subset_ip)}")
    col1A.dataframe(subset_ip)
    col2B.write("")
    bars = alt.Chart(subset_ip,title="Byte Distribution",height=350).mark_bar().encode(
                    x='Bytes',
                    y="count()",
                )
    col2B.altair_chart(bars,use_container_width=True)
The most important piece here in sharing between the two containers is

API_HOST = os.environ.get("API_HOST","http://localhost:7000")
The code reaches out for an environment variable

API_HOST
This will be set in our docker-compose.yml file on run time

Dashboard UI



Docker Container - Streamlit

There are a few requirements for the dashboard to run in a Docker environment.

Must have python installed

Must have necessary packages

Must have command than runs the dashboard

Must have the port exposed

Now that the requirements have been listed we can created our Dockerfile. In the following section we assume that you have all of these files in the same directory.

Python Image - Has python already installed

FROM python:3
Add scripts

ADD ./app.py /  
Install packages

In most cases we use a requirments.txt file and simply add all package names to it then run a command like a pip install -r requirments.txt command. In this case since we only need three libraries we won’t bother to build that out.

RUN pip install streamlit
RUN pip install pandas
RUN pip install requests
RUN pip install altair
Expose Port

Here we expose port 7000 so that we can connect the dashboard to the API.

EXPOSE 8502
Run the Dashboard

CMD ["streamlit","run","app.py","--server.port", "8502"]
Full Docker Script

FROM python:3 

ADD ./app.py / 

RUN pip install streamlit
RUN pip install pandas
RUN pip install requests
RUN pip install altair 

EXPOSE 8502 

CMD ["streamlit","run","app.py","--server.port", "8502"]
Docker-Compose

We now use docker-compose to run these two containers on the same docker network. Docker-compose makes it easier to orchestrate multiple containers.

docker-compose.yml

Assumes file structure is the same as in github repo:

current_directory
├───docker-compose.yml
├───api
├───dashboard
yaml file

version: "3"
services:
  substackapi:
    build: "./api"
    ports:
      - "7000:7000"
  substackdashboard:
    build: ./dashboard
    ports:
      - "8502:8502"
    environment:
      - API_HOST=http://substackapi:7000
    depends_on: 
      - substackapi 
Note:

API_HOST is set to http://substackapi:7000. This allows the dashboard to connect to the api container. We’ve named the service for the api “substackapi”. Had we named it something else this should be set to http://<nameyougaveservice>:7000

To launch you simply need to run:

docker-compose up
Assuming you are in the same directory as the docker-compose.yml file.

After launch you should be able to see the dashboard at:

http://localhost:8502

And the api dashboard at:

http://localhost:7000/docs
