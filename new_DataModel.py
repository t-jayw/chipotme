import re, sys, os, random
import pandas as pd
import requests as r

from pathlib import Path

import StoreLocator as sl

class DataHandler(object):
  req_columns = ['Date', 'Description', 'Original Description',
                'Amount', 'Transaction Type', 'Category']

  def __init__(self, df=pd.DataFrame(), rec_data=0):
    if not df.empty:
      self.raw_df = df
    else:
      self.raw_txns_path = '~/Downloads/transactions (3).csv'
      self.raw_df = pd.read_csv(self.raw_txns_path)
    self.store_records_path = 'data/chipotle_store_info.csv'
    self.store_records = pd.read_csv(self.store_records_path)
    if 'Unnamed: 0' in self.store_records.columns:
      self.store_records = self.store_records.drop('Unnamed: 0', axis=1)
    if not self.verify_columns():
      raise ValueError('Provided csv does not contain needed columns')
    self.pdf = self.gen_processed_df()
    self.store_records = self.enhance_with_StoreInfo()
    self.final_df = self.merge_txn_and_store_info()
    if rec_data == [1]:
      self.log_transactions(self.final_df)


  def log_transactions(self, df):
    file_unique = random.randint(0,10**8)
    file_path = 'data/anon/%s_chipotle_final.csv'%(str(file_unique))
    df.to_csv(file_path)


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
  
  def gen_processed_df(self):
    """spits out the final base df for graphs to use"""
    # Drop unnecessary columns
    pdf = self.drop_columns(self.raw_df) 
    # Pull chipotle txns
    pdf = self.extract_chipotle(pdf) 
    # convert to datetime
    pdf.Date = pd.to_datetime(pdf.Date)
    #Extract store no from descriptor
    pdf['store_no'] = pdf.loc[:,'Original Description'].apply( 
                      lambda x: self.parse_store_number(x))
    pdf['store_no_int'] = pdf.store_no.apply(lambda x: int(x))
    # reset index
    pdf.reset_index(inplace=True, drop=True)
    return pdf

  def enhance_with_StoreInfo(self): 
    ### Use StoreInfo object to add granular location detail
    already_checked = []

    srdf = self.store_records
    for x in self.pdf.store_no:
      x = int(x)
      if x not in list(srdf.store_no.apply(int))+already_checked:
        already_checked.append(x)
        store = sl.StoreInfo(x)
        new_row = store.get_new_store_record()
        if new_row:
          srdf.loc[len(srdf)] = new_row
        else: 
          print('problem making row')
      else:
        continue
    srdf.drop_duplicates().to_csv('data/chipotle_store_info.csv', index=False)
    return srdf
  
  def merge_txn_and_store_info(self):
    """merges the txn processed df and the store info df"""
    final_df = pd.merge(self.pdf, self.store_records.drop_duplicates(), 
                    left_on='store_no_int', right_on='store_no', how='left')
    final_df = final_df.drop('store_no_y', axis = 1)
    final_df.rename(columns={'store_no_x':'store_no_string','store_no_int':'store_no'}, inplace=True)
    return final_df



if __name__ == '__main__':
  foo = DataProcessor()

