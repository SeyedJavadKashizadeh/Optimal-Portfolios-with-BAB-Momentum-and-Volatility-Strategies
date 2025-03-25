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
import BAB
import plots
import momentum
import idio_vol

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#---------------------------------------------
# Downloading Data
#---------------------------------------------
"""
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
"""
#-------------------------------------------------------
# Rolling Beta Using Numba for Loop and Parquet Saving
#-------------------------------------------------------
project_path = 'G:/My Drive/EPFL/first_year/semester3/Investment/project'

raw_data = pd.read_csv("raw_data.csv",sep=";",nrows=10000)
sic_data = pd.read_csv("sic_data.csv",sep=";",nrows=10000)

data = raw_data.copy()
data = rolling_beta.beta_calculator(data, parquet_path=f'{project_path}/beta_parquet.parquet')

#----------------------------------------------------
# Betting Against Beta (Frazzini & Pedersen (2014))
#----------------------------------------------------
BAB_dataset = data.copy()
BAB_dataset, BAB_factor = BAB.bab_return(BAB_dataset)
plots.signal_returns(BAB_factor, 'date', 'BAB_return', 'BAB Factor (Frazzini & Pedersen (2014))', 'Value Weighted', saving_path=f'{project_path}/BAB.png')

#--------------------------------------------------------
# Momentum Strategy (Jegadeesh & Titman (1993))
#---------------------------------------------------------
mom_dataset = data.copy()
mom_factor = momentum.mom_return(mom_dataset)
plots.signal_returns(mom_factor, 'date', 'MOM_return', 'Momentum Factor (Jegadeesh & Titman (1993))', 'Value Weighted', saving_path=f'{project_path}/momentum.png')

#--------------------------------------------------------
# Idiosyncratic Strategy (Ang, Hodrick, Xing, and Zhang (2006))
#---------------------------------------------------------
idio_vol_dataset = data.copy()
idio_vol_factor = idio_vol.ivol_return(idio_vol_dataset)
plots.signal_returns(idio_vol_factor, 'date', 'IVOL_return', 'Idiosyncratic Factor (Ang, Hodrick, Xing, and Zhang (2006))', 'Value Weighted', saving_path=f'{project_path}/idio_vol.png')
