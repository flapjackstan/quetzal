# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 08:54:37 2022

@author: elmsc
https://pygis.io/docs/d_access_census.html
"""

from census import Census
from us import states
import pandas as pd

#%%

census = Census(CENSUS_API_KEY)

#%%

ca_census = census.acs5.state_county(fields = ('NAME'),
                                     state_fips = states.CA.fips,
                                     county_fips = "*",
                                     year = 2020,)



#%% 
# https://api.census.gov/data.html
# https://www.socialexplorer.com/data/ACS2019_5yr/metadata/?ds=ACS19_5yr
# https://www.census.gov/programs-surveys/acs/data.html
# https://www.census.gov/programs-surveys/acs/data/data-via-api.html



la_census = census.acs5.state_county_tract(fields = ('NAME'),
                                      state_fips = states.CA.fips,
                                      county_fips = "037",
                                      tract = "*",
                                      year = 2020,)

#%%


zip_census = census.acs5.state_zipcode(fields = ('NAME'),
                                      state_fips = states.CA.fips,
                                      zcta = "*",
                                      year = 2020,)

#%%


ca_df = pd.DataFrame(ca_census)
