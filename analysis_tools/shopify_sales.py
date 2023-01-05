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

from datetime import datetime, timedelta
from analysis_tools.shopify_api import read_json, get_line_items, get_count_orders, get_count_of_product, get_order_data, get_items_available


def is_void(order) -> bool:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    bool
        True if order is voided

    '''
    financial_status = order["data"]["orders"]["nodes"][0]["displayFinancialStatus"]
    
    if financial_status == "VOIDED":
        return True
    
    return False
     

def is_unfulfilled(order) -> bool:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    bool
        True if order is unfulfilled

    '''
    financial_status = order["data"]["orders"]["nodes"][0]["displayFulfillmentStatus"]
    
    if financial_status == "UNFULFILLED":
        return True
    
    return False


def has_tags(search_tags, tag_list) -> bool:
    '''
    

    Parameters
    ----------
    search_tags : list
        list of hashtags to look for in tag_list.
    
    tag_list : list
        list of hashtags to check.

    Returns
    -------
    bool
        True if tags are present.

    '''
    
    for tag in tag_list:
        if tag in search_tags:
            return True
        
    return False
        

def get_order_total_collected(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Money collected from transaction.

    '''
    
    if is_void(order) or is_unfulfilled(order) or has_tags(["test"], get_order_data(order)["tags"]):
        return(float(0))
    
    total_amount = order["data"]["orders"]["nodes"][0]["originalTotalPriceSet"]["shopMoney"]["amount"]
    
    return float(total_amount)


def get_customer_orders(order) -> list:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        List of customer orders including Tip

    '''
    
    return order["data"]["orders"]["nodes"][0]["lineItems"]["nodes"]


def get_tip_amount(order_list) -> float:
    '''

    Parameters
    ----------
    order_list : list
        customer orders list.

    Returns
    -------
    float
        Money collected from tips.

    '''
    
    for index, order in enumerate(order_list):
        
        if "Tip" in order["name"]:
            tip_amount = order["originalTotalSet"]["shopMoney"]["amount"]
        else:
            tip_amount = 0.0
    
    return float(tip_amount)


def get_order_tips(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Money collected from tips. If no tip is collected this is 0

    '''
    
    cutomer_orders = get_customer_orders(order)
    tip_amount = get_tip_amount(cutomer_orders)
    
    return tip_amount


def get_fee(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Fees Collected

    '''
    
    data = get_order_data(order)
    
    # some have empty transactions
    if not data["transactions"]:
        return 0.0
    
    # some paid cash and there is no fee
    if not data["transactions"][0]["fees"]:
        return 0.0

    return float(data["transactions"][0]["fees"][0]["amount"]["amount"])


def get_timeframe(timeframe_str) -> list:
    '''
    

    Parameters
    ----------
    timeframe_str : str
        timeframe split by comma.

    Returns
    -------
    list
        List with start timeframe and end timeframe.

    '''
    
    timeframe = timeframe_str.split(',')
    timeframe = [datetime.strptime(x, '%Y-%m-%d') for x in timeframe]
    
    return timeframe

def get_aggs(orders_list, timeframe) -> dict:
    '''

    Parameters
    ----------
    orders_dict : dict
        shopify order return

    Returns
    -------
    dict : agg_dict
        dictionary with summary aggregates

    '''
    
    timeframe = get_timeframe(timeframe)
    
    agg_dict = {}
    
    total_tips = 0
    total_collected = 0
    total_fees = 0
    total_cash_collected = 0
    order_count = 0
    
    items_available = get_items_available(orders_list)
    items_dict = {}
    
    for index, item in enumerate(items_available):
        entry = {}
        entry["product name"] = item
        entry["count"] = 0
        items_dict[index] = entry
    
    
    for index, order in enumerate(orders_list):
        
        pst = get_time_of_order(order)
        
        if timeframe[0].date() <= pst.date() <= timeframe[1].date():
        
            tip_amount = get_order_tips(order)

            for index, item in enumerate(items_available):
                items_dict[index]["count"] = items_dict[index]["count"] + get_count_of_product(order, item)
            
            
            total_tips = total_tips + tip_amount
                
            # MONEY COLLECTED AND FEES
            
            total_collected = total_collected + get_order_total_collected(order)
            total_fees = total_fees + get_fee(order)
    
            total_cash_collected = total_cash_collected + get_cash_collected(order)
            
            # SIMPLE COUNT OF ORDERS
            order_count = order_count + 1
        
    total_sales = total_collected - total_tips
        
    agg_dict.update({"Total Orders": order_count})
    agg_dict.update({"Total Collected": total_collected})
    agg_dict.update({"Total Tips Collected": total_tips})
    agg_dict.update({"Total Sales": total_sales})
    agg_dict.update({"Total Fees": total_fees})
    agg_dict.update({"Total Paid in Cash": total_cash_collected})
    agg_dict.update({"Total Paid in Credit": total_collected - total_cash_collected})
    agg_dict.update({"Product Dictionary": items_dict})
    
    return agg_dict




def get_transaction_gateway(order):
    
    data = get_order_data(order)
    
    # some have empty transactions
    if not data["transactions"]:
        return 0.0
    
    return data["transactions"][0]["gateway"]


def get_cash_collected(order):
    
    gateway = get_transaction_gateway(order)
    
    if gateway == "cash":
        return float(get_order_total_collected(order))
    
    return 0

def orders_to_df(orders_list):
    '''
    

    Parameters
    ----------
    orders_list : list
        Shopify orders list

    Returns
    -------
    df : DataFrame
        Dataframe version of orders
    '''
    
    data_list = []
    
    for index, order in enumerate(orders_list):
        data_list.append(get_order_data(order))
        
    return pd.DataFrame(data_list)


def add_event_variables(order_list, events) -> list:
    '''

    Parameters
    ----------
    orders_list : list
        Shopify orders list
        
    events : dict
        dictionary of dates: event name

    Returns
    -------
    orders_list : list
        Shopify orders list with added event variable and product collab variables

    '''
    
    mod_order_list = []
    
    for index, order in enumerate(order_list):

        pst = get_time_of_order(order)
        pst_str = pst.strftime('%Y-%m-%d')
   
        # I can use a hashmap method here because no transformation to keys are needed
        try:
            order["data"]["orders"]["nodes"][0]["event"] = events[pst_str]
        except KeyError:
            order["data"]["orders"]["nodes"][0]["event"] = "Non Event"
            
        mod_order_list.append(order)
        
    return mod_order_list
        
def add_collab_variables(order_list, collabs) -> list:
    '''
    TODO
    write docstring for collabs
    write access funcs for each variable
    
    Parameters
    ----------
    orders_list : list
        Shopify orders list
        
    events : dict
        dictionary of dates: event name

    Returns
    -------
    orders_list : list
        Shopify orders list with added event variable and product collab variables

    '''
    
    mod_order_list = []
    
    for index, order in enumerate(order_list):
        
        order["data"]["orders"]["nodes"][0]["collab"] = "No Collaboration"

        pst = get_time_of_order(order)
        
        # Will probably have to do this by product and date, not just date
        for index, collab in enumerate(collabs):
            timeframe = get_timeframe(collab["collab_timeframe"])

            # this needs a conditional that checks if varable exists and if it has another event name already (none or no collaboration ok)
            if timeframe[0].date() <= pst.date() <= timeframe[1].date() and order["data"]["orders"]["nodes"][0]["collab"] == "No Collaboration":
                order["data"]["orders"]["nodes"][0]["collab"] = collab["collab_name"]
                
            
        mod_order_list.append(order)
        
    return mod_order_list


def get_time_of_order(order):
    '''
    

    Parameters
    ----------
    order : dict
        Shopify order

    Returns
    -------
    date : dt
    datetime obj in pst

    '''
    
    # utc is 8hrs ahead of pst
    utc = datetime.strptime(get_order_data(order)["processedAt"], '%Y-%m-%dT%H:%M:%SZ')
    pst = utc - timedelta(hours=8, minutes=0)
    
    return pst


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
november_orders = read_json(data_path, "november_orders", ".json")

# #%%

# events = {"2022-11-05":"Compton Farmers Market",
#           "2022-11-15":"USC Trojan Market",
#           "2022-12-03":"DTSA: Santora Artwalk",
#           "2022-12-04":"Ten Mile Brewery",          
#           "2022-12-18":"Cherry Co. Farmers Market"
#           }

# collabs = [
#               {"collab_timeframe":"2022-12-03,2022-12-03", "collab_name":"16% of Can Sales Buy Toys"},
#               {"collab_timeframe":"2022-12-04,2022-12-04", "collab_name":"100% of Hot Chocolate and Beans Go to Blackdog"}       
#           ]

# # this func needs to accept below format
# december_orders = add_event_variables(december_orders, events)

# december_orders = add_collab_variables(december_orders, collabs)

# dec = orders_to_df(december_orders)

# december_orders_aggs = get_aggs(december_orders, "2022-12-01,2022-12-31")

#%%

# one above needs to be changed to this format
dec_events = {
    0:{"timeframe":"2022-12-03,2022-12-03", "event name":"DTSA: Santora Artwalk", "cost of event" : 0, "address": "207 N Broadway, Santa Ana, CA, 92701", "coords": "3.7465567,-117.8715178"},
    1:{"timeframe":"2022-12-04,2022-12-04", "event name":"Ten Mile Brewery", "cost of event" : 0, "address": "1136 E Willow St, Signal Hill, CA 90755", "coords": "3.8039489,-118.17998"},          
    2:{"timeframe":"2022-12-18,2022-12-18", "event name":"Cherry Co. Farmers Market", "cost of event" : 35, "address": "211 Avenida Del Norte, Redondo Beach, CA 90277", "coords": "33.8184134,-118.389958"}
    }

for index, event in enumerate(dec_events):
    dec_events[index]["aggs"] = get_aggs(december_orders, dec_events[index]["timeframe"])
    
# one above needs to be changed to this format
nov_events = {
    0:{"timeframe":"2022-11-05,2022-11-05", "event name":"Compton Farmers Market"},
    1:{"timeframe":"2022-11-15,2022-11-15", "event name":"USC Trojan Market"}
    }

for index, event in enumerate(nov_events):
    nov_events[index]["aggs"] = get_aggs(november_orders, nov_events[index]["timeframe"])
    
