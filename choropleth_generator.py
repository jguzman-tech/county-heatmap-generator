import geopandas as gpd
import folium
import requests
import pandas as pd
import fiona
import branca
import json
import numpy as np
import pdb # put pdb.set_trace() anywhere 
import ast
import copy
import plotly.express as px
from urllib.request import urlopen

def parse_inner_county_data(data):
    data = ast.literal_eval(data)
    return data['fips']['County']

url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
# geo-dataframe
gdf = gpd.read_file(url)

# county-dataframe
cdf = pd.read_csv('2018_11_04_21_stream_1_clean_mord_loc_fips_data.csv', sep='\t')
fips_series = cdf['fips'].apply(parse_inner_county_data) # promote inner dictionary
fips_df = fips_series.apply(pd.Series) # expand inner dict

# basic processing
fips_df['FIPS'] = fips_df['FIPS'].apply(pd.to_numeric)
fips_df = fips_df.dropna() # ignore if the fip number is invalid
fips_df = fips_df.reset_index(drop=True) # start indices from 0 again
fips_df['FIPS'] = fips_df['FIPS'].astype(int)
fips_df = fips_df.rename(columns={'FIPS':'fips'})

old = fips_df.apply(copy.deepcopy)

# create a 'hits' column and consilidate all repeats based on fips
# the county name isn't necessarily unique but the fips number is
# so base hits on the fips number
# this link shows the most common county names:
# https://en.wikipedia.org/wiki/List_of_the_most_common_U.S._county_names
# for example there are 12 counties named Polk
temp_fips_hits = fips_df['fips'].value_counts(sort=True).apply(copy.deepcopy)
fips_df.drop_duplicates(subset='fips', inplace=True)
fips_df = fips_df.reset_index(drop=True) # start indices from 0 again

fips_df['hits'] = -1
for fips in temp_fips_hits.index:
    fips_df['hits'][fips_df['fips'] == fips] = temp_fips_hits[fips]
# fips_df['hits'] = temp_fips_hits

print(f"processing {fips_df.shape[0]} out of {cdf.shape[0]} data points")
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

fig = px.choropleth(fips_df, geojson=counties, locations='fips', color='hits',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           labels={'fips':'fips', 'name':'name', 'hits':'hits'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#fig.show()
fig.write_html('index.html')
