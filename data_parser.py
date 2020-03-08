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

def parse_inner_county_data(data):
    data = ast.literal_eval(data)
    return data['fips']['County']

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Parse dataset into a smaller python dataframe file'
    )
    parser.add_argument("in_file", help="input filename")
    parser.add_argument("out_file", help="output filename")
    args = parser.parse_args()

    # county-dataframe
    cdf = pd.read_csv(args.in_file, sep='\t')
    # promote inner dictionary
    fips_series = cdf['fips'].apply(parse_inner_county_data)
    # expand inner dict
    fips_df = fips_series.apply(pd.Series)

    # basic processing
    fips_df['FIPS'] = fips_df['FIPS'].apply(pd.to_numeric)
    fips_df = fips_df.dropna() # ignore if the fip number is invalid
    fips_df = fips_df.reset_index(drop=True) # start indices from 0 again
    fips_df['FIPS'] = fips_df['FIPS'].astype(int)
    fips_df = fips_df.rename(columns={'FIPS':'fips'})
    print(f"processing {fips_df.shape[0]} out of {cdf.shape[0]} data points")

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

    fips_df.to_pickle(args.out_file)
