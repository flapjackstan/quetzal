#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 03:01:43 2023

@author: camargo
"""

import pandas as pd
import geopandas as gpd
import folium
from census import Census
from us import states
from spatial_tools.census_api import getCounties, xy_to_points
from analysis_tools.shopify_api import read_json, get_aggs


def split_coords_to_lat_long(coords):
    lat_longs = coords.split(",")
    
    return lat_longs

#%%
data_path = "./data/"
december_orders = read_json(data_path, "december_orders", ".json")

# dec_events = {
#     0:{"timeframe":"2022-12-03,2022-12-03", "event name":"DTSA: Santora Artwalk", "cost of event" : 0, "address": "207 N Broadway, Santa Ana, CA, 92701", "coords": "3.7465567,-117.8715178"},
#     1:{"timeframe":"2022-12-04,2022-12-04", "event name":"Ten Mile Brewery", "cost of event" : 0, "address": "1136 E Willow St, Signal Hill, CA 90755", "coords": "3.8039489,-118.17998"},          
#     2:{"timeframe":"2022-12-18,2022-12-18", "event name":"Cherry Co. Farmers Market", "cost of event" : 35, "address": "211 Avenida Del Norte, Redondo Beach, CA 90277", "coords": "33.8184134,-118.389958"}
#     }

dec_events = pd.read_csv("./data/december_events.csv")

dec_events["lat"] = dec_events['coords'].apply(lambda x: split_coords_to_lat_long(x)[0])
dec_events["long"] = dec_events['coords'].apply(lambda x: split_coords_to_lat_long(x)[1])

dec_events = xy_to_points(dec_events, "long", "lat")

#%%

ca_tracts = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_06_tract.zip")

county_fips = getCounties()
la_fips = county_fips["Los Angeles"]
lacounty_tracts = ca_tracts.query('COUNTYFP == @la_fips')

#%%

polygon_map = lacounty_tracts.explore(color=None, name="tracts")

polygon_and_points_map = dec_events.explore(m=polygon_map, color="#a31010", name="event points")

folium.TileLayer("CartoDB positron", control=True).add_to(polygon_and_points_map)
folium.LayerControl().add_to(polygon_and_points_map)
polygon_and_points_map.save("map.html")

# for index, event in enumerate(dec_events):
#     dec_events[index]["aggs"] = get_aggs(december_orders, dec_events[index]["timeframe"])