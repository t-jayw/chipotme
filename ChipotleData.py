import re, sys, os
import pandas as pd
import requests as r
import zipcodes as zc
import matplotlib.pyplot as plt

from pathlib import Path
from bs4 import BeautifulSoup as bs

def pull_span_zip(span_text:str, store_no:str):
    pat = '^%s'%(store_no)
    if re.match(pat, span_text):
        zipcode = re.findall(' (\d{5})', span_text)
        return zipcode[0]
    else:
        return None
    
def search_chip_no(store_no:str):
    chip_job_url = "https://jobs.chipotle.com/search-jobs/%s"%(str(store_no))
    cont = bs(r.get(chip_job_url).content, 'html5lib')
    spans = cont.find_all('span')
    lines = [span.get_text() for span in spans]
    for x in lines: 
        zipc = pull_span_zip(x, store_no)
        if zipc:
            break
    
    return [store_no, zipc, x]
            
def chip_txns(df:pd.DataFrame, regex):
    df = df[df['Original Description'].str.contains(regex)]
    return df

def parse_store_loc(descriptor:str):
    nos = re.findall(' (\d{4})', descriptor)
    return nos[0]

def pull_lat_long(zipcode:str):
    try:
        return [zc.matching(zipcode)[0]['lat'],
                  zc.matching(zipcode)[0]['long']]
    except:
        return [None,None]

def main_df_setup(file_path):
    df = pd.read_csv(file_path)
    df.drop(columns=['Category','Labels', 'Notes'], inplace=True)
    
    # LIMIT TO CHIPOTLE TXNS
    cdf = chip_txns(df, 'CHIPOTLE')
    # EXTRACT STORE NO
    cdf['store_no'] = cdf.loc[:,'Original Description'].apply(lambda x: parse_store_loc(x))
    # RESET INDEX
    cdf.reset_index(inplace=True, drop=True)

    # Pull Location Info
    print('fetching zips')
    zip_addr = cdf.store_no.apply(search_chip_no)
    zip_df = pd.DataFrame(list(zip_addr), columns=['store_no','zip_code','address'])
    # CONCAT zip_df cols to cdf
    tdf = pd.concat([cdf, zip_df], axis=1)

    # GET LAT LONS
    latlons = tdf.zip_code.apply(pull_lat_long)
    latlons_df = pd.DataFrame(list(latlons),columns=['lat', 'long'])
    # CONCAT latlons df cols to cdf
    ldf = pd.concat([tdf, latlons_df], axis=1)

    return ldf

if __name__ == '__main__':
    file_path = Path(sys.argv[1])
    
    output = Path('data/chipotle_df.csv')
    os.makedirs(os.path.dirname(output), exist_ok=True)

    if output.is_file():
        print("data already loaded")
    else:
        df = main_df_setup(file_path)
        df.to_csv(output)

    print("--done--")









    


