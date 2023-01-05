#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 03:01:43 2023

@author: camargo
"""

import pandas as pd
from analysis_tools.shopify_api import read_json

#%%
data_path = "./data/"
december_orders = read_json(data_path, "december_orders", ".json")

dec_events = {
    0:{"timeframe":"2022-12-03,2022-12-03", "event name":"DTSA: Santora Artwalk", "cost of event" : 0, "address": "207 N Broadway, Santa Ana, CA, 92701", "coords": "3.7465567,-117.8715178"},
    1:{"timeframe":"2022-12-04,2022-12-04", "event name":"Ten Mile Brewery", "cost of event" : 0, "address": "1136 E Willow St, Signal Hill, CA 90755", "coords": "3.8039489,-118.17998"},          
    2:{"timeframe":"2022-12-18,2022-12-18", "event name":"Cherry Co. Farmers Market", "cost of event" : 35, "address": "211 Avenida Del Norte, Redondo Beach, CA 90277", "coords": "33.8184134,-118.389958"}
    }

dec_events_copy = pd.read_csv("./data/december_events.csv")

for index, event in enumerate(dec_events):
    dec_events[index]["aggs"] = get_aggs(december_orders, dec_events[index]["timeframe"])