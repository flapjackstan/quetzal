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

#%%

load_dotenv()
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")

SHOP_NAME = "tazacafe"
API_VERSION = '2022-10'

#%%

shop_url = f"{SHOP_NAME}.myshopify.com"
# query = "{ shop { name id } }"

query = """{
  orders(first: 10) {
    edges {
      node {
        id
        updatedAt
        lineItems(first: 10) {
          edges {
            node {
              id
              name
            }
          }
        }
        customer {
          id
          displayName
        }
      }
    }
  }
}

"""

with shopify.Session.temp(shop_url, API_VERSION, SHOPIFY_ADMIN_TOKEN):
    query_return = json.loads(shopify.GraphQL().execute(query))

#%%

query_return["data"]["orders"]["edges"][4]["node"]
