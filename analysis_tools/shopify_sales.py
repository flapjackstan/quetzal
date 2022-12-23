#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 12:31:00 2022

@author: camargo
"""
#%%
import os
from dotenv import load_dotenv
import shopify
import json
from pathlib import Path

#%%

def read_file_as_text(path):
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
    return file_text


#%%

load_dotenv()

SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "tazacafe"
SHOP_URL = f"{SHOP_NAME}.myshopify.com"
API_VERSION = '2022-10'

#%%

query = read_file_as_text("analysis_tools/queries/orders.gql")

#%%

with shopify.Session.temp(SHOP_URL, API_VERSION, SHOPIFY_ADMIN_TOKEN):
    # below converts shopify return json (not ecma-262) into a python dict
    query_return = json.loads(shopify.GraphQL().execute(query))
    # below converts the python dict into a json (ecma-262) that is able to be uploaded to postgres
    valid_json = json.dumps(query_return["data"]["orders"]["nodes"])

#%%





