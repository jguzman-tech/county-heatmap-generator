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
import pickle

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Combine a direcotry of .pkl files'
    )
    parser.add_argument("input_dir",
                        help="directory to search for .pkl files to combine")
    parser.add_argument("out_file", help="output filename")
    args = parser.parse_args()

    pattern = os.path.join(args.input_dir, "*.pkl")

    all_pd = pd.DataFrame(columns=['fips', 'name', 'hits'])
    # indexing a dict is about 100x faster than a DataFrame
    all_hits = dict()
    count = 0
    print("about to enter pattern")
    my_glob = glob.glob(pattern)
    for f in my_glob:
        small_pd = pd.read_pickle(f)
        for i in range(small_pd.shape[0]):
            fips = small_pd['fips'].loc[i]
            name = small_pd['name'].loc[i]
            hits = small_pd['hits'].loc[i]
            # try and except should be faster than checking if key exists
            try:
                all_hits[fips][0] += hits
            except:
                all_hits[fips] = [hits, name]
        count += 1
        print(f"processed {count} files out of {len(my_glob)}")

    # copy dict info to all_pd
    for key in all_hits:
        fips = str(key)
        fips = fips.zfill(5) # 0 padded
        hits = all_hits[key][0]
        name = all_hits[key][1]
        if name.find("County") == -1:
            name += " County"
        all_pd = all_pd.append({'fips':fips, 'name':name, 'hits':hits},
                      ignore_index=True)

    all_pd = all_pd.astype({'fips':'str', 'name':'str', 'hits':'int'})
    print(f"writing to file")
    all_pd.to_pickle(args.out_file)
