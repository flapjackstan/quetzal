#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 09:14:39 2022

@author: camargo
"""
#%% imports
import pandas as pd
import re

#%%

def transaction_to_float(transaction):
    """

    Parameters
    ----------
    transaction : str
        string containing cash transaction

    Returns
    -------
    float
        amount of cash transaction

    """
    
    # no cash sign no whitespace
    list_of_char =['$', '\s']
    
    pattern = '[' + ''.join(list_of_char) + ']'
    mod_string = re.sub(pattern, '', transaction)

    return float(mod_string)

def get_venmo_sales(venmo_csv, year_month):
    """

    Parameters
    ----------
    year_month : str
        date string to filter

    Returns
    -------
    total_sales
        summed amount of sales
        
        #%% special events
        event_0_string = "2022-11-05"
        event_0 = venmo[venmo['date'].dt.strftime('%Y-%m-%d') == event_0_string]

        event_1_string = "2022-11-15"
        event_1 = venmo[venmo['date'].dt.strftime('%Y-%m-%d') == event_1_string]
        
        # # filter by single month
        # venmo = venmo[venmo['date'].dt.strftime('%Y-%m') == '2014-01']

        # # filter by single year
        # venmo = venmo[venmo['date'].dt.strftime('%Y') == '2014']

    """
    
    venmo = pd.read_csv(venmo_csv, skiprows=[0,1])
    
    # use this later maybe
    
    # begin_balance = venmo["Beginning Balance"][0]
    # end_balabce = venmo["Ending Balance"][len(venmo)-1]
    
    # arrange data to be able to clean and filter
    venmo = venmo.drop(labels=[0, len(venmo)-1], axis=0)
    
    # put in correct data types
    venmo["amount"] = venmo["Amount (total)"].apply(transaction_to_float)
    venmo["date"] = pd.to_datetime(venmo['Datetime'])
    
    # remove non sales related data - need to auto mate the id one somehow
    venmo = venmo.query("Type != 'Standard Transfer'")
    venmo = venmo.query("amount > 0")
    venmo = venmo.query("ID != 3672941199591778304")
    
    # keep only useful data
    keep_cols = ['ID', 'date', 'Note', 'From', 'amount']
    venmo = venmo[keep_cols]
    
    venmo = venmo[venmo['date'].dt.strftime('%m-%Y') == year_month]
    
    total_sales = venmo["amount"].sum()

    return total_sales

def get_shopify_sales(shopify_csv, year_month):
    """

    Parameters
    ----------
    year_month : str
        date string to filter

    Returns
    -------
    total_sales
        summed amount of sales

    """
    
    shopify_csv = "data/orders_export_1.csv"
    
    shopify = pd.read_csv(shopify_csv)
    
    
    

#%%
    
if __name__ == "__main__":
    get_venmo_sales("data/transaction_history.csv", "11-2022")

