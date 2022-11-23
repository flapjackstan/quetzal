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
    # no cash sign no whitespace
    list_of_char =['$', '\s']
    
    pattern = '[' + ''.join(list_of_char) + ']'
    mod_string = re.sub(pattern, '', transaction)

    return float(mod_string)


#%% read

venmo = pd.read_csv("../data/transaction_history.csv", skiprows=[0,1])

#%% amount toal string to float and date conversion

venmo["amount"] = venmo["Amount (total)"].apply(transaction_to_float)
venmo["date"] = pd.to_datetime(venmo['Datetime'])

#%% get begin and end

begin_balance = venmo["Beginning Balance"][0]
end_balabce = venmo["Ending Balance"][len(venmo)-1]

#%% drop first and last row

venmo = venmo.drop(labels=[0, len(venmo)-1], axis=0)

#%% useful columns

keep_cols = ['ID', 'date', 'Note', 'From', 'amount']

venmo = venmo[keep_cols]

#%% clean non sales related obs

venmo = venmo.query("Type != 'Standard Transfer'")
venmo = venmo.query("amount > 0")



