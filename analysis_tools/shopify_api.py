# -*- coding: utf-8 -*-

import shopify
import json
import os
from dotenv import load_dotenv

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