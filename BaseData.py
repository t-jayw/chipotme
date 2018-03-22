### you're getting distracted, come back to this later

import re, sys, os
import pandas as pd
import requests as r

from pathlib import Path

class ChipModel(object):
  def __init__(self, filepath):
    self.df = pd.read_csv(filepath)
    self.column_req = ['Date', 'Description', 'Original Description']
  def validate(self, df):
    
  
  def fetch_storeno(self, df):
    if "store_no" in columns:
      return
    else:
      ### Go get the store number ###
      return


