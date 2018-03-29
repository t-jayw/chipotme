import glob, os

import pandas as pd

### Script to replace 'data/default.csv' with updates from uploaded data
### to anon by users

path = 'data/anon/'
print(path)

all_files = glob.glob(os.path.join(path, "*.csv")) #make list of paths
print(all_files)

df_from_each_file = (pd.read_csv(f) for f in all_files)
concatenated_df   = pd.concat(df_from_each_file, ignore_index=True)

concatenated_df.drop_duplicates(inplace=True)

concatenated_df.to_csv('data/default.csv')