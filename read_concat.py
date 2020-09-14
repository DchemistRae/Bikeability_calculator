import pandas as pd
import glob
import os

#Read in files
path = r'dataframes1' # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    df['city'] = os.path.basename(filename.split('_')[0])
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

#Write to file
frame.to_csv('cities_segments_df.csv', index = False)