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

#%%

load_dotenv()
SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOPIFY_API_KEY = os.environ.get("SHOPIFY_API_KEY")
SHOPIFY_SECRET_KEY = os.environ.get("SHOPIFY_SECRET_KEY")
SHOPIFY_PASSWORD = os.environ.get("SHOPIFY_PASSWORD")

SHOP_NAME = "tazacafe"


#%%

shop_url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin"

shopify.ShopifyResource.set_site(shop_url)


#%%

# =============================================================================
# {
#   orders(first: 10) {
#     edges {
#       node {
#         id
#         updatedAt
#         lineItems (first: 10){
#           edges {
#             node {
#               id
#               name
#             }
#           }
#         }
#         customer {
#           id
#           displayName
#         }
#       }
#     }
#   }
# }
# =============================================================================
