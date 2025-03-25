#---------------------------------------------
# Libraries
#---------------------------------------------

# Built-in libraries
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import wrds
import time

#  user-written modules
import loading_data
import rolling_beta

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#---------------------------------------------
# Downloading Data
#---------------------------------------------

db=wrds.Connection(wrds_username='javadkashizadeh')

# Load data
Rf = loading_data.rf_rate(db)
Rm = loading_data.market_ret(db)
sic_data = loading_data.sic_data(db)
sic_data = sic_data.drop_duplicates(subset=['permno', 'date'], keep='last')
sic_data.to_csv('sic_data.csv', sep=';', index=False)

stock_data = loading_data.stock_data(db)
stock_data = stock_data.drop_duplicates(subset=['permno', 'date'], keep='last')
# Merge and prepare final dataset
data = pd.merge(stock_data, Rf, on='date', how='left')
data = pd.merge(data, Rm, on='date', how='left')
data['const'] = 1
data['Rn_e'] = data['Rn'] - data['rf']
data['Rm_e'] = data['Rm'] - data['rf']
# Export
data.to_csv('raw_data.csv', sep=';', index=False)

#-------------------------------------------------------
# Rolling Beta Using Numba for Loop and Parquet Saving
#-------------------------------------------------------
project_path = 'G:/My Drive/EPFL/first_year/semester3/Investment/project'

raw_data = pd.read_csv("raw_data.csv",sep=";")
sic_data = pd.read_csv("sic_data.csv",sep=";")

data = raw_data.copy()
data2 = rolling_beta.beta_calculator(data, parquet_path=f'{project_path}/beta_parquet.parquet')
