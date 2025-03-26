import numpy as np
import pandas as pd

def risk_parity(data, window=12):

    factors = data[['BAB_return', 'MOM_return', 'IVOL_return']]
    volatility = factors.rolling(window=window).std()
    inv_vol = 1 / volatility
    rp_weights = inv_vol.div(inv_vol.sum(axis=1), axis=0).dropna()

    risk_p = factors.copy()
    common_dates = rp_weights.index.intersection(risk_p.index)
    rp_weights = rp_weights.loc[common_dates]
    risk_p = risk_p.loc[common_dates]

    risk_p['rp_return'] = (rp_weights * risk_p).sum(axis=1)
    risk_p['date'] = data.loc[common_dates, 'date'].values

    return risk_p[['date', 'rp_return']]

def mean_variance(data, window=12):
    factors = ['BAB_return', 'MOM_return', 'IVOL_return']
    rolling_cov = data[factors].rolling(window=window).cov().dropna()
    rolling_mean = data[factors].rolling(window=window).mean().dropna()
    inv_cov = rolling_cov.groupby(level=0).apply(lambda x: np.linalg.inv(x)).reset_index(level=0, drop=True)
    common_dates = rolling_mean.index.intersection(inv_cov.index)

    weight_list = []
    for date in common_dates:
        one_cov = inv_cov.loc[date]
        one_return = rolling_mean.loc[date]
        weights = one_cov @ one_return
        weights /= weights.sum()
        weights_df = pd.DataFrame(weights).T
        weights_df.index = [date]
        weight_list.append(weights_df)

    all_weights = pd.concat(weight_list)
    mean_var =  data[factors]
    risk_p = risk_parity(data)

    # date index modified
    common_dates = all_weights.index.intersection(risk_p.index)
    mean_var = mean_var.loc[common_dates]
    all_weights.columns = factors  # add column names

    mean_var.loc[:, 'mv_return'] = (all_weights * mean_var[factors]).sum(axis=1)
    mean_var['date'] = data.loc[common_dates, 'date'].values

    return mean_var



def fund_return(BAB_factor,mom_factor,idio_vol_factor):

    fund_portfolio = BAB_factor
    fund_portfolio = fund_portfolio.merge(mom_factor, on='date', how='inner').merge(idio_vol_factor, on='date', how='inner')
    fund_portfolio['equal_return'] = fund_portfolio[['BAB_return', 'MOM_return', 'IVOL_return']].mean(axis=1)

    risk_p = risk_parity(fund_portfolio)
    fund_portfolio = fund_portfolio.merge(risk_p[['rp_return','date']], on='date', how='inner')

    mean_var = mean_variance(fund_portfolio)
    fund_portfolio = fund_portfolio.merge(mean_var[['mv_return','date']], on='date', how='inner')

    annual_volatility = fund_portfolio[['equal_return', 'rp_return', 'mv_return']].std() * np.sqrt(12)
    target_volatility = 0.1
    multipliers = target_volatility / annual_volatility
    adj_ret = fund_portfolio[['equal_return', 'rp_return', 'mv_return']].mul(multipliers, axis=1)
    adj_ret.columns = [col + '_adj' for col in adj_ret.columns]
    fund_portfolio = pd.concat([fund_portfolio, adj_ret], axis=1)

    return fund_portfolio