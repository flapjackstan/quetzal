import os
from dotenv import load_dotenv
import shopify
import json
import pandas as pd
from pathlib import Path

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
#%%


load_dotenv()

data_path = "./data/"
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "tazacafe"
API_VERSION = '2022-10'

SHOP_URL = f"{SHOP_NAME}.myshopify.com"
#%%
query = '''

{
  shopifyPaymentsAccount {
    id
    chargeStatementDescriptors{default}
  }
}

'''

gql = execute_gql(gql=query, json_return=0, variables=None)
print(gql["data"])
print(gql["errors"])