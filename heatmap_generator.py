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
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Parse dataset into a smaller python dataframe file'
    )
    parser.add_argument("in_file", help="data filename")
    parser.add_argument("out_file", help="output heatmap filename (.html)")
    parser.add_argument("--logarithmic",
                        action='store_true',
                        dest="logarithmic",
                        help=("set this argument if you want the 'heat'" +
                              "to be on a logarithmic scale instead of linear"))
    args = parser.parse_args()

    fips_df = pd.read_pickle(args.in_file)

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    fips_df['name'] = fips_df['name'] + " County"
    max_heat = fips_df.hits.quantile(0.9)
    if(args.logarithmic):
        fips_df['hits'] = fips_df['hits'].apply(np.log)
        max_heat = fips_df['hits'].max()
    fig = px.choropleth(fips_df, geojson=counties, locations='fips', color='hits',
                        color_continuous_scale="Viridis",
                        range_color=(0, max_heat),
                        scope="usa",
                        hover_name="name",
                        hover_data=['name'],
                        labels={'fips':'fips', 'hits':'hits'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html(args.out_file)
