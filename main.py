# Built-in libraries
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import wrds
import time

#  user-written modules
import loading_data
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


db=wrds.Connection(wrds_username='javadkashizadeh')

# Load data
Rf = loading_data.rf_rate(db)
Rm = loading_data.market_ret(db)
stock_data = loading_data.stock_data(db)

# Merge and prepare final dataset
data = pd.merge(stock_data, Rf, on='date', how='left')
data = pd.merge(data, Rm, on='date', how='left')
data['const'] = 1
data['Rn_e'] = data['Rn'] - data['rf']
data['Rm_e'] = data['Rm'] - data['rf']

# Export
data.to_csv('raw_data.csv', sep=';', index=False)
