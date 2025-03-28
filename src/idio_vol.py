import pandas as pd
import numpy as np

def idio_vol_rolling(data):

    df = data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['resid_CAPM'] = df['Rn_e'] - df['alpha'] - df['Rm_e'] * df['beta_original']
    df['resid_CAPM_lag'] = df.groupby('permno')['resid_CAPM'].shift(1)

    rolling_ivol = df.set_index('date').groupby('permno')['resid_CAPM_lag'] .rolling(window=60, min_periods=36).std().reset_index(name='Rolling_std')
    df = df.merge(rolling_ivol, on=['permno', 'date'], how='left')
    lower = df['Rolling_std'].quantile(0.05)
    upper = df['Rolling_std'].quantile(0.95)
    df['Rolling_std'] = df['Rolling_std'].clip(lower=lower, upper=upper)

    return df

def ivol_return(data):

    df = idio_vol_rolling(data)

    df['ivol_rank'] = df.groupby('date')['Rolling_std'].transform(lambda x: pd.qcut(x, 10, labels=False, duplicates='drop') + 1)
    df['vw'] = df.groupby(['date', 'ivol_rank'])['mcap'].transform(lambda x: x / x.sum())
    df['weighted_ret'] = df['Rn'] * df['vw']
    dec_ret = df.groupby(['date', 'ivol_rank'], group_keys=False)['weighted_ret'].sum().reset_index(name='ret_vw')
    short = dec_ret[dec_ret['ivol_rank'] <= 3].groupby('date')['ret_vw'].mean()
    long = dec_ret[dec_ret['ivol_rank'] >= 8].groupby('date')['ret_vw'].mean()
    ivol_vw = (long - short).reset_index(name='IVOL_return')

    return ivol_vw, short, long

