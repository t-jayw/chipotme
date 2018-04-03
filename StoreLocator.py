import re, sys, os
import pandas as pd
import requests as r
import zipcodes as zc

from pathlib import Path
from bs4 import BeautifulSoup as bs

class StoreInfo(object):
  chip_job_url = "https://jobs.chipotle.com/search-jobs/%s"
  gotem = []
  def __init__(self, store_no):
    self.store_no = store_no
    #self.set_store_info(store_no)

  def store_string_pad(self):
    store_no_string = str(self.store_no)
    self.store_no_string = '0'*(4-len(store_no_string)) + store_no_string

  def pull_span_zip(self, span_text, store_no):
    pat = "(^|^0*)%s"%(store_no)
    if re.match(pat, span_text):
      zipcode = re.findall(' (\d{5})', span_text)
      return zipcode[len(zipcode)-1]
    else:
      return None

  def fetch_store_info(self):
    output = 'None', 'None'
    url = self.chip_job_url%(str(self.store_no))
    cont = bs(r.get(url).content, 'html5lib')
    spans = cont.find_all('span')
    lines = [span.get_text() for span in spans]
    if lines:
      for x in lines:
        zipc = self.pull_span_zip(x, self.store_no)
        if zipc:
          output = zipc, x
          return output
        else:
          continue
    return output

  def pull_loc_info(self, zipcode):
    try:
      zcmatch = zc.matching(str(zipcode))[0]
      return zcmatch
    except:
      return {}
  
  def set_store_info(self, store_no, record_df):
    store_no = self.store_no
    self.add_new_store_record() ## This should go get the relevant info
      
  def get_new_store_record(self):
    store_no = self.store_no
    ### I don't have a record for this store
    ### so I proceed to
    columns = ['store_no','zip_code','address','lat','lon','city','state']
    zipcode, location_span = self.fetch_store_info()
    zc_match = self.pull_loc_info(zipcode)
    if len(zc_match) > 0:
      zc_match['store_no'] = store_no
      zc_match['lon'] = zc_match['long']
      zc_match['address'] = location_span
      dict_row = {c:zc_match[c] for c in columns}
      dict_row['short_address'] = re.sub('\w* - .* -','',location_span)
      return dict_row
    else:
      print("couldn't find store")
      return None

  def get_store_info(self):
    col_names = ['store_no', 'zip_code', 'address', 'lat', 'lon', 'city', 'state']
    x =  [self.store_no, self.zip, self.address, 
            self.lat, self.lon, self.city, self.state]
    return zip(col_names, x)
