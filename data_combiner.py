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
import glob, os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Combine two .pkl files'
    )
    parser.add_argument("input_dir",
                        help="directory to search for .pkl files to combine")
    parser.add_argument("out_file", help="output filename")
    args = parser.parse_args()

    pattern = os.path.join(args.input_dir, "*.pkl")
    
    all_pd = pd.DataFrame()
    count = 0
    print("about to enter pattern")
    my_glob = glob.glob(pattern)
    for f in my_glob:
        if(count == 0):
            all_pd = pd.read_pickle(f)
        else:
            pd1 = pd.read_pickle(f)
            unique_fips = pd.concat([all_pd['fips'], pd1['fips']]).unique()
            new_pd = pd.DataFrame(columns=['fips', 'name', 'hits'])
            new_pd['fips'] = new_pd['fips'].astype(int)
            new_pd['hits'] = new_pd['hits'].astype(int)
            for fips in unique_fips:
                search = all_pd[all_pd['fips'] == fips]
                success = False
                if(search.shape[0] == 1):
                    success = True
                    index = search.index[0]
                    new_pd = new_pd.append(all_pd.iloc[index], ignore_index=True)
                search = pd1[pd1['fips'] == fips]
                if(search.shape[0] == 1):
                    index = search.index[0]
                    if(success):
                        new_pd['hits'][new_pd.shape[0] - 1] += pd1['hits'][index]
                    else:
                        new_pd = new_pd.append(pd1.iloc[index], ignore_index=True)
            all_pd = new_pd
        count += 1
        print(f"processed {count} files out of {len(my_glob)}")

    print(f"writing to file")
    all_pd.to_pickle(args.out_file)
