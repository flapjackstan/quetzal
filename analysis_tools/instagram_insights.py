#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 18:54:14 2022

@author: camargo
"""

#%%

import os
from dotenv import load_dotenv

# https://github.com/adw0rd/instagrapi
from instagrapi import Client

#%%

load_dotenv()

INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")


#%%

# https://adw0rd.github.io/instagrapi/usage-guide/insight.html
# https://github.com/adw0rd/instagrapi/blob/master/instagrapi/mixins/insights.py

cl = Client()
cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

test1= cl.insights_media_feed_all("ALL", "ONE_WEEK", "REACH_COUNT")
test2 = cl.insights_account()
