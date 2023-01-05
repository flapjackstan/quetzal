# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 08:54:37 2022

@author: elmsc
https://pygis.io/docs/d_access_census.html
"""
import os
from dotenv import load_dotenv

import geopandas as gpd
from census import Census
from us import states
import pandas as pd

import requests
import csv
import folium

#%%
load_dotenv()

CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY")
census = Census(CENSUS_API_KEY)

#%%

# https://gist.github.com/cjwinchester/a8ff5dee9c07d161bdf4 
# above contains code to get adjacent counties as well
def getCounties():
    "Function to return a dict of FIPS codes (keys) of U.S. counties (values)"
    d = {}
    r = requests.get("http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt")
    reader = csv.reader(r.text.splitlines(), delimiter=',')    
    for line in reader:
        d[line[3].replace(" County","")] = line[2] # adding line 1 gets state fips
    return d


def xy_to_points(df, longitude_string, latitude_string):
    """

    Parameters
    ----------
    df : pandas df
        dataframe with x and y

    Returns
    -------
    points : geopandas gdf
        Geodataframe with points
        
    References
    -------
    https://geopandas.org/en/stable/gallery/create_geopandas_from_pandas.html
    
    Todo
    -------
    

    """
    points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[longitude_string], df[latitude_string]))
    points = points.set_crs('epsg:4269')
    return points

county_fips = getCounties() 

#%%

# ca_census = census.acs5.state_county(fields = ('NAME'),
#                                      state_fips = states.CA.fips,
#                                      county_fips = "*",
#                                      year = 2020,)



# #%% 
# # https://api.census.gov/data.html
# # https://www.socialexplorer.com/data/ACS2019_5yr/metadata/?ds=ACS19_5yr
# # https://www.census.gov/programs-surveys/acs/data.html
# # https://www.census.gov/programs-surveys/acs/data/data-via-api.html



# la_census = census.acs5.state_county_tract(fields = ('NAME'),
#                                       state_fips = states.CA.fips,
#                                       county_fips = county_fips["Los Angeles"],
#                                       tract = "*",
#                                       year = 2020,)

# #%%


# zip_census = census.acs5.state_zipcode(fields = ('NAME'),
#                                       state_fips = states.CA.fips,
#                                       zcta = "*",
#                                       year = 2020,)

# #%%


# ca_df = pd.DataFrame(ca_census)


# #%%

# ca = states.lookup("CA")
# print(ca.shapefile_urls("tract"))

# #%% Close to above but for 2022

# ca_tracts = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_06_tract.zip")

# #%% https://sparkbyexamples.com/pandas/pandas-dataframe-query-examples/
# la_fips = county_fips["Los Angeles"]
# lacounty_tracts = ca_tracts.query('COUNTYFP == @la_fips')

# #%%
# airbnb_points = gpd.read_file("../datasci/mlr_airbnb/airbnb_points.geojson")

# #%%

# tract_map = lacounty_tracts.explore(name="LA County Tracts")
# tract_map.save("tracts.html")


# #%%

# airbnb_map = airbnb_points.explore(color="red", name="Airbnb Locations")
# airbnb_map.save("airbnb_points.html")

# #%% https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html

# tracts_and_points_map = lacounty_tracts.explore(m=airbnb_map, name="LA County Tracts")
# #%%

# folium.TileLayer('CartoDB positron', control=True).add_to(tracts_and_points_map)  # use folium to add alternative tiles
# folium.LayerControl().add_to(tracts_and_points_map)
# #%%
# tracts_and_points_map.save("points_and_polygons.html")



