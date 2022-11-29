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

def get_sales(transaction):
    """

    Parameters
    ----------
    month_year : str
        date string to filter

    Returns
    -------
    total_sales
        summed amount of sales

    """
    
    venmo = pd.read_csv("../data/transaction_history.csv", skiprows=[0,1])
    
    # use this later maybe
    
    # begin_balance = venmo["Beginning Balance"][0]
    # end_balabce = venmo["Ending Balance"][len(venmo)-1]
    
    # arrange data to be able to clean and filter
    venmo = venmo.drop(labels=[0, len(venmo)-1], axis=0)
    
    # put in correct data types
    venmo["amount"] = venmo["Amount (total)"].apply(transaction_to_float)
    venmo["date"] = pd.to_datetime(venmo['Datetime'])
    
    # remove non sales related data
    venmo = venmo.query("Type != 'Standard Transfer'")
    venmo = venmo.query("amount > 0")
    venmo = venmo.query("ID != 3672941199591778304")
    
    # keep only useful data
    keep_cols = ['ID', 'date', 'Note', 'From', 'amount']
    venmo = venmo[keep_cols]


    return float(mod_string)

def main():


    #%% special events
    event_0_string = "2022-11-05"
    event_0 = venmo[venmo['date'].dt.strftime('%Y-%m-%d') == event_0_string]

    event_1_string = "2022-11-15"
    event_1 = venmo[venmo['date'].dt.strftime('%Y-%m-%d') == event_1_string]


    #%%

    venmo["amount"].sum()


    # # filter by single month
    # venmo = venmo[venmo['date'].dt.strftime('%Y-%m') == '2014-01']

    # # filter by single year
    # venmo = venmo[venmo['date'].dt.strftime('%Y') == '2014']
    
    

