# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 15:11:22 2022

@author: ryan.gilmore
"""

from typing import Optional

from fastapi import FastAPI


import pandas as pd

from pydantic import BaseModel

description = """
Substack API
API that connects to DNS Data
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

@app.get('/data/{bytes}',tags=['data'])
def subset_by_bytes(b:int):
    subset = df[df['Bytes'] > b]
    subset.index = range(0,len(subset))
    return subset.to_json()

@app.post('/data/ip',tags=['data'])
def subset_by_ip(ipclass: IP):
    subset = df[df['IP'] == ipclass.ip]
    subset.index = range(0,len(subset))
    return subset.to_json()
