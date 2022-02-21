# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 20:23:54 2022

@author: ryan.gilmore
"""

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


