#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 12:31:00 2022

@author: camargo
"""
#%% Functions and Libraries

import os
from dotenv import load_dotenv
import shopify
import json
import pandas as pd
from pathlib import Path

def read_file_as_text(path) -> str:
    """
    Parameters
    ----------
    path  :   str
    path to file to be read
    
    Returns
    -------
    file_text    :   str
    text from file
    
    Example
    -------
    read_sql("my_file.gql")
        "query { shop { name id } }"
    """
    file_text = Path(path).read_text(encoding="utf-8")
    
    # error handling?
    
    return file_text


def convert_dict_to_json(py_dict) -> str:
    """
    Parameters
    ----------
    py_dict  :   dict
    dict to convert to json
    
    Returns
    -------
    json_return    :   str
    json version of dict
    
    Example
    -------
    convert_dict_to_json({key:"value"})
        "{key:"value"}"
    """
    json_return = json.dumps(py_dict)
    
    # error handling?
    
    return json_return


def execute_gql(gql, variables, json_return=0):
    """
    Parameters
    ----------
    gql  :   str
    gql to be executed
    
    Returns
    -------
    query_return    :   dict | str
    text from file
    
    Example
    -------
    execute_gql("query { shop { name id } }")
        {shop: tazacafe}
    """
    
    with shopify.Session.temp(SHOP_URL, API_VERSION, SHOPIFY_ADMIN_TOKEN):

        # below converts shopify return json (not ecma-262) into a python dict
        query_return = json.loads(shopify.GraphQL().execute(gql, variables=variables))
        
    if json_return:
        # below converts the python dict into a json (ecma-262) that is able to be uploaded to postgres
        query_return = convert_dict_to_json(query_return["data"])
    
    # error handling?
    
    return query_return


def get_orders_between_dates(date_1, date_2) -> list:
    """
    Parameters
    ----------
    date_1  :   str
    Begin date filter
    
    date_2  :   str
    End date fiter
    
    Returns
    -------
    query_return    :   dict | str
    text from file
    
    Example
    -------
    get_orders_between_dates("2022-12-01", "2022-12-31")
        orders return from shopify
    """
    
    print(f"Getting orders between {date_1} and {date_2}")
    
    query = read_file_as_text("analysis_tools/queries/orders.gql")
    date_filter = f"processed_at:>{date_1} AND processed_at:<{date_2}"
    input_vars = {"user_query": date_filter}
    
    first_return = execute_gql(gql=query, json_return=0, variables=input_vars)
    
    has_next_page = first_return["data"]["orders"]["pageInfo"]["hasNextPage"]
    end_cursor = first_return["data"]["orders"]["pageInfo"]["endCursor"]
    
    print(f"Has Next Page: {has_next_page}")
    # print(f"End Cursor: {end_cursor}")
    
    return_list = []
    return_list.append(first_return)
    
    while has_next_page and len(return_list) < 100:
        
        query = read_file_as_text("analysis_tools/queries/keep_getting_orders.gql")
        date_filter = f"processed_at:>{date_1} AND processed_at:<{date_2}"
        input_vars = {"user_query": date_filter, "prev_cursor": end_cursor}
        
        shopify_returns = execute_gql(gql=query, json_return=0, variables=input_vars)
        print(shopify_returns["data"]["orders"]["nodes"][0]["name"])
        return_list.append(shopify_returns)
        
        has_next_page = shopify_returns["data"]["orders"]["pageInfo"]["hasNextPage"]
        end_cursor = shopify_returns["data"]["orders"]["pageInfo"]["endCursor"]
        
        # print(f"Has Next Page: {has_next_page}")
        # print(f"End Cursor: {end_cursor}")
        print(f"Request Number: {len(return_list)}")
    
    query_return = return_list
    
    # error handling?
    
    return query_return


def write_file(obj, path, filename, ext) -> None:
    '''
    Parameters
    ----------
    obj : df | dict
        Object to write.
    path : Path object
        Path object / destination.
    filename : str
        Name of file to write
    ext : str
        File type extension.

    Returns
    -------
    None.
    '''
    
    write_path = Path(path)

    with open(write_path.joinpath(filename + ext), "w+") as f:
        json.dump(obj, f)
        

def read_json(path, filename, ext) -> dict:
    '''
    
    Parameters
    ----------
    path : Path object
        Path object / destination.
    filename : str
        Name of file to write
    ext : str
        File type extension.

    Returns
    -------
    dict
        json converted to dictionary

    '''
    
    read_path = Path(path)
    
    with open(read_path.joinpath(filename + ext)) as json_file:
        data = json.load(json_file)
        
    return json.loads(data)


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
        print(financial_status)
        return True
    
    return False


def has_tags(tag_list) -> bool:
    '''
    

    Parameters
    ----------
    tag_list : list
        list of hashtags to check.

    Returns
    -------
    bool
        True if tags are present.

    '''


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
    
    if is_void(order) or is_unfulfilled(order):
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


def get_aggs(orders_list) -> dict:
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
    
    agg_dict = {}
    
    total_tips = 0
    customer_tip_count = 0
    total_collected = 0
    total_cash_collected = 0
    total_credit_collected = 0
    order_count = 0
    
    for index, order in enumerate(orders_list):
        
        # TIPS CALCULATION
        tip_amount = get_order_tips(order)
        
        if tip_amount > 0:
            customer_tip_count = customer_tip_count + 1
            
        total_tips = total_tips + tip_amount
            
        # TOTAL MONEY COLLECTED
        
        total_collected = total_collected + get_order_total_collected(order)
        # total_cash_collected = total_cash_collected + get_cash_collected(order)
        # total_credit_collected = total_credit_collected + get_credit_collected(order)
        
        
        
        # SIMPLE COUNT OF ORDERS
        order_count = order_count + 1
        
    total_sales = total_collected - total_tips
        
    agg_dict.update({"Total Orders": order_count})
    agg_dict.update({"Total Collected": total_collected})
    agg_dict.update({"Total Tips Collected": total_tips})
    agg_dict.update({"Total Customers Who Tipped": customer_tip_count})
    agg_dict.update({"Total Sales": total_sales})
    
    return agg_dict


def access_order_data(order) -> dict:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    dict
        data dict from individual order.

    '''
    
    return order["data"]["orders"]["nodes"][0]


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
        data_list.append(access_order_data(order))
        
    return pd.DataFrame(data_list)

    

#%%
#%% Constants

load_dotenv()

data_path = "./data/"
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "tazacafe"
API_VERSION = '2022-10'

SHOP_URL = f"{SHOP_NAME}.myshopify.com"

events = {"Compton Farmers Market":"2022-11-05",
          "USC Trojan Market":"2022-11-15",
          "DTSA: Santora Artwalk":"2022-12-03",
          "Ten Mile Brewery":"2022-12-04",          
          "Cherry Co. Farmers Market":"2022-12-18"
          }


#%% Example Filter Query

# orders(first: 15, query: "created_at:>2022-12-18") #the date string needs to be updatable
# orders(first: 1, query: "name:#1085") # two orders and tip, no customer name
# orders(first: 1, query: "name:#1005") # one order and customer name

query = read_file_as_text("analysis_tools/queries/orders.gql")
input_vars = {"user_query": "processed_at:>2022-11-01"}
gql = execute_gql(gql=query, json_return=0, variables=input_vars)

#%%

november_orders = get_orders_between_dates("2022-11-01", "2022-11-30")
# december_orders = get_orders_between_dates("2022-12-01", "2022-12-31")

# data_path = "./data/"
# november_orders = read_json(data_path, "november_orders", ".json")
# december_orders = read_json(data_path, "december_orders", ".json")

# #%%
# november_orders_json = convert_dict_to_json(november_orders)
# decemer_orders_json = convert_dict_to_json(december_orders)

# write_file(november_orders_json, data_path, "november_orders", ".json")
# write_file(decemer_orders_json, data_path, "december_orders", ".json")

#%%

df = orders_to_df(november_orders)

#%%

november_orders_aggs = get_aggs(november_orders)
# december_orders_aggs = get_aggs(december_orders)

#%%

# Need to filter on refunded
november_transactions = november_orders_aggs["Total Cash Collected"] - 180 
december_transactions = december_orders_aggs["Total Cash Collected"]

#%%

customer_transactions_to_date = november_transactions + december_transactions
shopify_percent = .027
gabby_percent = .05
elmer_percent = .05

revenue_to_date = customer_transactions_to_date

shopify_payout = revenue_to_date * shopify_percent 

revenue_after_shopify = revenue_to_date - shopify_payout

gabby_payout = revenue_after_shopify * gabby_percent

revenue_after_gabby = revenue_to_date - gabby_payout

elmer_payout = revenue_after_gabby * elmer_percent

revenue_after_elmer = revenue_after_gabby - elmer_payout
