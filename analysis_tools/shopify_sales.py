#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 12:31:00 2022
notes
Shopify pay out .027
Gabby buy in 3393.51
Elmer buy in 3340.95


use dates, products and percentage donation to calculate how much goes to other person

calc average monthly spend
@author: camargo
"""
#%% Functions and Libraries

import os
from dotenv import load_dotenv
import shopify
import pandas as pd


from analysis_tools.shopify_api import read_json, add_event_variables, add_collab_variables, get_aggs, orders_to_df

#%% Constants

load_dotenv()

data_path = "./data/"
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "tazacafe"
API_VERSION = '2022-10'

SHOP_URL = f"{SHOP_NAME}.myshopify.com"


#%% Example Filter Query

# orders(first: 15, query: "created_at:>2022-12-18") #the date string needs to be updatable
# orders(first: 1, query: "name:#1085") # two orders and tip, no customer name
# orders(first: 1, query: "name:#1005") # one order and customer name

# query = read_file_as_text("analysis_tools/queries/orders.gql")
# input_vars = {"user_query": "processed_at:>2022-11-01"}
# gql = execute_gql(gql=query, json_return=0, variables=input_vars)

#%%

# november_orders = get_orders_between_dates("2022-11-01", "2022-11-30")
# december_orders = get_orders_between_dates("2022-12-01", "2022-12-31")

# # #%%
# november_orders_json = convert_dict_to_json(november_orders)
# decemer_orders_json = convert_dict_to_json(december_orders)

# write_file(november_orders_json, data_path, "november_orders", ".json")
# write_file(decemer_orders_json, data_path, "december_orders", ".json")

#%%

data_path = "./data/"
december_orders = read_json(data_path, "december_orders", ".json")

events = {"2022-11-05":"Compton Farmers Market",
          "2022-11-15":"USC Trojan Market",
          "2022-12-03":"DTSA: Santora Artwalk",
          "2022-12-04":"Ten Mile Brewery",          
          "2022-12-18":"Cherry Co. Farmers Market"
          }

collabs = [
              {"collab_timeframe":"2022-12-03,2022-12-03", "collab_name":"16% of Can Sales Buy Toys"},
              {"collab_timeframe":"2022-12-04,2022-12-04", "collab_name":"100% of Hot Chocolate and Beans Go to Blackdog"}       
          ]

# # this func needs to accept "YYYY-MM-DD,YYYY-MM-DD"
december_orders = add_event_variables(december_orders, events)

december_orders = add_collab_variables(december_orders, collabs)

dec = orders_to_df(december_orders)

december_orders_aggs = get_aggs(december_orders, "2022-12-01,2022-12-31")

