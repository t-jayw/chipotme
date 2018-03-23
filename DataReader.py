import re, sys, os
import pandas as pd
import requests as r

from pathlib import Path

import StoreLocator as sl

class DataReader(object):
  req_columns = ['Date', 'Description', 'Original Description',
                'Amount', 'Transaction Type', 'Category']

  def __init__(self):
    self.raw_txns_path = '~/Downloads/transactions (3).csv'
    self.store_records = 'data/chipotle_store_info.csv'
    self.raw_df = pd.read_csv(self.raw_txns_path)
    self.store_records = pd.read_csv(self.store_records)
    if not self.verify_columns():
      raise ValueError('Provided csv does not contain needed columns')
    self.pdf = self.gen_processed_df()


  def verify_columns(self):
    raw_cols = self.raw_df.columns
    if set(type(self).req_columns).issubset(raw_cols):
      return True
    else:
      print("Missing necessary columns: %s"%(str(type(self).req_columns)))
      return False
    
  def drop_columns(self, vdf):
    """drop unnecessary cols"""
    drop_cols = set(vdf.columns) - set(type(self).req_columns)
    return vdf.drop(columns=drop_cols)

  def extract_chipotle(self, vdf):
    """pull chipotle txns"""
    return vdf[vdf['Original Description'].str.contains('CHIPOTLE')]

  def parse_store_number(self,descriptor):
    """parse descriptor to extract store no"""
    re_match = re.findall(' (\d{4})', descriptor)
    return re_match[0]
   
  def gen_location_info(self, store_no, store_records):
    store = sl.StoreInfo(store_no, self.store_records)
    loc_info = store.get_store_info()
    return loc_info

  def record_loc_info_df(self):
    updated_store_records = self.loc_info_df.drop_duplicates()
    updated_store_records = updated_store_records.reset_index(drop=True)
    updated_store_records.to_csv('data/chipotle_store_info.csv')
  
  def gen_processed_df(self):
    """spits out the final base df for graphs to use"""
    pdf = self.drop_columns(self.raw_df)
    pdf = self.extract_chipotle(pdf)
    pdf.Date = pd.to_datetime(pdf.Date) # convert to datetime
    pdf['store_no'] = pdf.loc[:,'Original Description'].apply(
                      lambda x: self.parse_store_number(x))
    pdf['store_no_int'] = pdf.store_no.apply(lambda x: int(x))
    pdf.reset_index(inplace=True, drop=True)
    ### Use StoreInfo object to add granular location detail
    _loc_info = pdf.store_no.apply(lambda x: self.gen_location_info(x,
    self.store_records))
    self.loc_info_df = pd.DataFrame(list(_loc_info),   
                                columns=['store_no','zip_code', 'address', 'lat', 'lon',
                                'city', 'state'])
    pdf = pdf.join(self.loc_info_df, rsuffix='_')
    print(pdf.head())
    print(pdf.address[1])
    print(type(pdf.address[1]))
    pdf['short_address'] = pdf.address.apply(lambda x: re.sub('\w* - .* -','',
                                                            x.value()))
    self.record_loc_info_df()
    return pdf

if __name__ == '__main__':
  foo = DataProcessor()
  print(foo.pdf.head())
